import os
import numpy as np
import pandas as pd

# Define paths
SOURCE_WORKBOOK = "data/raw/urban_cart_retail_dataset.xlsx"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("=" * 70)
print("Starting data cleaning and transformation pipeline...")
print("=" * 70)

# --- 1. Load Source Sheets ---
print(f"Loading multi-sheet workbook: {SOURCE_WORKBOOK}")
excel_reader = pd.ExcelFile(SOURCE_WORKBOOK)

df_customers = excel_reader.parse("dim_customers")
df_darkstores = excel_reader.parse("dim_darkstores")
df_products = excel_reader.parse("dim_products")
df_orders = excel_reader.parse("fact_orders")

print(f"    - Customers: {df_customers.shape[0]} rows, {df_customers.shape[1]} cols")
print(f"    - Darkstores: {df_darkstores.shape[0]} rows, {df_darkstores.shape[1]} cols")
print(f"    - Products: {df_products.shape[0]} rows, {df_products.shape[1]} cols")
print(f"    - Orders: {df_orders.shape[0]} rows, {df_orders.shape[1]} cols")

# --- 2. Type Casting & String Sanitization ---
print("\nReconciling data types and sanitizing strings...")

# Clean dim_customers
df_customers["customer_id"] = df_customers["customer_id"].astype(str).str.strip()
df_customers["customer_segment"] = df_customers["customer_segment"].astype(str).str.strip()
df_customers["city_tier"] = df_customers["city_tier"].astype(str).str.strip()
df_customers["lifetime_rewards_tier"] = df_customers["lifetime_rewards_tier"].astype(str).str.strip()
df_customers["signup_date"] = pd.to_datetime(df_customers["signup_date"])

# Clean dim_darkstores
df_darkstores["hub_id"] = df_darkstores["hub_id"].astype(str).str.strip()
df_darkstores["hub_name"] = df_darkstores["hub_name"].astype(str).str.strip()
df_darkstores["city"] = df_darkstores["city"].astype(str).str.strip()
df_darkstores["daily_operating_cost"] = df_darkstores["daily_operating_cost"].astype(float)
df_darkstores["target_sla_minutes"] = df_darkstores["target_sla_minutes"].astype(int)

# Clean dim_products
df_products["product_id"] = df_products["product_id"].astype(str).str.strip()
df_products["product_name"] = df_products["product_name"].astype(str).str.strip()
df_products["category"] = df_products["category"].astype(str).str.strip()
df_products["unit_cost"] = df_products["unit_cost"].astype(float)
df_products["listing_price"] = df_products["listing_price"].astype(float)

# Clean fact_orders
df_orders["order_id"] = df_orders["order_id"].astype(str).str.strip()
df_orders["customer_id"] = df_orders["customer_id"].astype(str).str.strip()
df_orders["product_id"] = df_orders["product_id"].astype(str).str.strip()
df_orders["hub_id"] = df_orders["hub_id"].astype(str).str.strip()
df_orders["order_timestamp"] = pd.to_datetime(df_orders["order_timestamp"])
df_orders["delivered_timestamp"] = pd.to_datetime(df_orders["delivered_timestamp"])
df_orders["order_status"] = df_orders["order_status"].astype(str).str.strip().str.upper()
df_orders["payment_method"] = df_orders["payment_method"].astype(str).str.strip()

numeric_order_cols = [
    "quantity", "gross_sales", "item_cost", "promo_discount",
    "delivery_fee_charged", "actual_delivery_cost", "payment_gateway_fee",
    "sla_delay_minutes"
]
for col in numeric_order_cols:
    df_orders[col] = pd.to_numeric(df_orders[col], errors="coerce").fillna(0.0)

# Preserve null ratings for cancelled orders
df_orders["customer_rating"] = pd.to_numeric(df_orders["customer_rating"], errors="coerce").astype("Int64")

# --- 3. Statistical Outlier Detection & IQR Treatment ---
print("\nAuditing and treating fulfillment SLA outliers via IQR...")

# Calculate IQR only on delivered or returned orders
delivered_mask = df_orders["order_status"].isin(["DELIVERED", "RETURNED"])
q1 = df_orders.loc[delivered_mask, "sla_delay_minutes"].quantile(0.25)
q3 = df_orders.loc[delivered_mask, "sla_delay_minutes"].quantile(0.75)
iqr = q3 - q1
upper_cap = float(q3 + (2.5 * iqr))

outlier_count = (df_orders.loc[delivered_mask, "sla_delay_minutes"] > upper_cap).sum()
print(f"    - Q1: {q1:.1f}m | Q3: {q3:.1f}m | IQR: {iqr:.1f}m | Upper Bound: {upper_cap:.1f}m")
print(f"    - Detected {outlier_count} extreme delay outliers. Capping to upper boundary.")

# Cast to float to safely apply winsorized upper bound
df_orders["sla_delay_treated"] = df_orders["sla_delay_minutes"].astype(float)
df_orders.loc[delivered_mask & (df_orders["sla_delay_minutes"] > upper_cap), "sla_delay_treated"] = upper_cap

# --- 4. Vectorized Unit Economics Calculations ---
print("\nComputing vectorized unit economic metrics...")

# Net Sales
df_orders["net_sales"] = np.round(df_orders["gross_sales"] - df_orders["promo_discount"], 2)

# Contribution Margin 1 (CM1) = Net Sales - Item Direct Cost
df_orders["cm1_gross_margin"] = np.round(df_orders["net_sales"] - df_orders["item_cost"], 2)

# Net Logistics Balance = Delivery Fee Charged - Actual Fleet Cost
df_orders["net_logistics_balance"] = np.round(df_orders["delivery_fee_charged"] - df_orders["actual_delivery_cost"], 2)

# Contribution Margin 2 (CM2) = CM1 + Net Logistics Balance - PG Fee
df_orders["cm2_variable_profit"] = np.round(
    df_orders["cm1_gross_margin"] + df_orders["net_logistics_balance"] - df_orders["payment_gateway_fee"], 2
)

# For cancelled orders, variable revenue and direct costs are zeroed out
cancelled_mask = df_orders["order_status"] == "CANCELLED"
df_orders.loc[cancelled_mask, ["net_sales", "cm1_gross_margin", "cm2_variable_profit"]] = 0.0

# Safe division for CM2 %
df_orders["cm2_margin_pct"] = np.where(
    df_orders["net_sales"] > 0,
    np.round((df_orders["cm2_variable_profit"] / df_orders["net_sales"]) * 100, 2),
    0.0
)

# Binary order-level profitability flag
df_orders["is_profitable"] = (df_orders["cm2_variable_profit"] > 0).astype(int)

# --- 5. Export Clean Datasets for PostgreSQL & Power BI ---
print("\nExporting cleaned production files to CSV...")

df_customers.to_csv(f"{PROCESSED_DIR}/dim_customers_clean.csv", index=False)
df_darkstores.to_csv(f"{PROCESSED_DIR}/dim_darkstores_clean.csv", index=False)
df_products.to_csv(f"{PROCESSED_DIR}/dim_products_clean.csv", index=False)
df_orders.to_csv(f"{PROCESSED_DIR}/fact_orders_clean.csv", index=False)

print("Data pipeline complete. Ready for PostgreSQL ingestion and statistical testing.")
print("=" * 70)