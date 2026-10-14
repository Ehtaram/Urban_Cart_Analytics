import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Set random seed for repeatable data generation
np.random.seed(42)
random.seed(42)

os.makedirs("data/raw", exist_ok=True)
FILE_PATH = "data/raw/urban_cart_retail_dataset.xlsx"

print("Generating synthetic UrbanCart retail dataset...")


# --- 1. Customer Dimension (dim_customers) ---
customer_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, 1201)]
signup_start = datetime(2025, 1, 1)
signup_dates = [
    signup_start + timedelta(days=random.randint(0, 365)) for _ in customer_ids
]
segments = np.random.choice(
    ["Value Hunter", "Convenience Seeker", "Premium Organic", "Bulk Buyer"],
    size=1200,
    p=[0.40, 0.30, 0.20, 0.10],
)
city_tiers = np.random.choice(
    ["Tier-1 Metro", "Tier-2 Emerging"], size=1200, p=[0.75, 0.25]
)
rewards_tiers = np.random.choice(
    ["Bronze", "Silver", "Gold", "Platinum"],
    size=1200,
    p=[0.55, 0.25, 0.15, 0.05],
)

df_customers = pd.DataFrame(
    {
        "customer_id": customer_ids,
        "signup_date": signup_dates,
        "customer_segment": segments,
        "city_tier": city_tiers,
        "lifetime_rewards_tier": rewards_tiers,
    }
)

# --- 2. Darkstore Hub Dimension (dim_darkstores) ---
hub_ids = [f"HUB_{str(i).zfill(2)}" for i in range(1, 16)]
cities = [
    "Bangalore",
    "Bangalore",
    "Bangalore",
    "Mumbai",
    "Mumbai",
    "Mumbai",
    "Delhi NCR",
    "Delhi NCR",
    "Delhi NCR",
    "Hyderabad",
    "Hyderabad",
    "Pune",
    "Pune",
    "Chennai",
    "Kolkata",
]
hub_names = [
    "Indiranagar Express",
    "Koramangala Darkstore",
    "Whitefield Hub",
    "Bandra Core",
    "Andheri Logistics",
    "Powai Fulfillment",
    "Gurugram Sector-29",
    "Noida Hub 18",
    "South Ex Express",
    "Hitec City Depot",
    "Gachibowli Logistics",
    "Kothrud Express",
    "Viman Nagar Hub",
    "T-Nagar Warehouse",
    "Salt Lake Terminal",
]
daily_operating_costs = [
    32000.0,
    35000.0,
    28000.0,
    42000.0,
    39000.0,
    31000.0,
    36000.0,
    29000.0,
    33000.0,
    30000.0,
    27000.0,
    24000.0,
    26000.0,
    29000.0,
    25000.0,
]
target_slas = [15, 15, 20, 15, 20, 20, 15, 20, 15, 15, 20, 20, 20, 15, 20]

df_darkstores = pd.DataFrame(
    {
        "hub_id": hub_ids,
        "hub_name": hub_names,
        "city": cities,
        "daily_operating_cost": daily_operating_costs,
        "target_sla_minutes": target_slas,
    }
)

# --- 3. Product Catalog Dimension (dim_products) ---
product_ids = [f"SKU_{str(i).zfill(4)}" for i in range(1, 251)]
categories_pool = [
    "Fresh Produce",
    "Dairy & Bakery",
    "Staples & Grains",
    "Snacks & Beverages",
    "Household & Cleaning",
    "Personal Care",
    "Instant & Frozen Foods",
]
assigned_categories = np.random.choice(categories_pool, size=250)

product_names = []
unit_costs = []
listing_prices = []

for idx, cat in enumerate(assigned_categories):
    p_id = idx + 1
    if cat == "Fresh Produce":
        cost = round(random.uniform(15.0, 120.0), 2)
        margin = random.uniform(1.15, 1.40)
        name = f"Produce Item {p_id}"
    elif cat == "Dairy & Bakery":
        cost = round(random.uniform(25.0, 250.0), 2)
        margin = random.uniform(1.10, 1.25)
        name = f"Dairy Baked {p_id}"
    elif cat == "Staples & Grains":
        cost = round(random.uniform(80.0, 850.0), 2)
        margin = random.uniform(1.08, 1.20)
        name = f"Staples Pack {p_id}"
    elif cat == "Snacks & Beverages":
        cost = round(random.uniform(20.0, 180.0), 2)
        margin = random.uniform(1.25, 1.60)
        name = f"Beverage Snack {p_id}"
    elif cat == "Household & Cleaning":
        cost = round(random.uniform(60.0, 450.0), 2)
        margin = random.uniform(1.30, 1.70)
        name = f"Home Clean {p_id}"
    elif cat == "Personal Care":
        cost = round(random.uniform(45.0, 650.0), 2)
        margin = random.uniform(1.35, 1.85)
        name = f"Personal Care {p_id}"
    else:
        cost = round(random.uniform(50.0, 320.0), 2)
        margin = random.uniform(1.20, 1.50)
        name = f"Frozen Food {p_id}"

    price = round(cost * margin, 2)
    product_names.append(name)
    unit_costs.append(cost)
    listing_prices.append(price)

df_products = pd.DataFrame(
    {
        "product_id": product_ids,
        "product_name": product_names,
        "category": assigned_categories,
        "unit_cost": unit_costs,
        "listing_price": listing_prices,
    }
)

# --- 4. Order Transactions Fact (fact_orders) ---
total_orders = 7000
order_ids = [f"ORD_{str(i).zfill(6)}" for i in range(1, total_orders + 1)]

# Orders placed between 6:00 AM and 11:00 PM
base_date = datetime(2025, 1, 1, 6, 0, 0)
order_timestamps = []
for _ in range(total_orders):
    random_days = random.randint(0, 410)
    random_seconds = random.randint(0, 61200)
    order_timestamps.append(
        base_date + timedelta(days=random_days, seconds=random_seconds)
    )

order_timestamps.sort()

chosen_customers = np.random.choice(customer_ids, size=total_orders)
chosen_products = np.random.choice(product_ids, size=total_orders)
chosen_hubs = np.random.choice(hub_ids, size=total_orders)

# Fast attribute lookup
prod_map = df_products.set_index("product_id").to_dict("index")
hub_map = df_darkstores.set_index("hub_id").to_dict("index")

quantities = np.random.choice([1, 2, 3, 4, 5], size=total_orders, p=[0.45, 0.30, 0.15, 0.07, 0.03])
gross_sales = []
unit_costs_incurred = []
promo_discounts = []
delivery_fees_charged = []
actual_delivery_costs = []
payment_gateway_fees = []
payment_methods = []
order_statuses = []
delivered_timestamps = []
customer_ratings = []
sla_delay_minutes = []

payment_pool = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
payment_weights = [0.60, 0.20, 0.10, 0.05, 0.05]

for i in range(total_orders):
    p_id = chosen_products[i]
    h_id = chosen_hubs[i]
    qty = quantities[i]

    unit_p = prod_map[p_id]["listing_price"]
    unit_c = prod_map[p_id]["unit_cost"]

    line_gross = round(unit_p * qty, 2)
    line_cost = round(unit_c * qty, 2)

    # Markdown tiers
    discount_pct = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.25], p=[0.30, 0.30, 0.20, 0.12, 0.08])
    discount = round(line_gross * discount_pct, 2)

    # Free delivery threshold at 399
    del_fee = 0.0 if line_gross >= 399.0 else 30.0

    # Fleet fulfillment payout per drop
    base_del_cost = random.uniform(35.0, 65.0)

    # Delivery duration and delay calculation
    target_sla = hub_map[h_id]["target_sla_minutes"]
    actual_duration = int(np.random.normal(loc=target_sla + 2, scale=8))
    actual_duration = max(8, actual_duration)

    delay = max(0, actual_duration - target_sla)
    sla_delay_minutes.append(delay)

    # Order lifecycle and doorstep cancellations on heavy delay
    status = np.random.choice(["DELIVERED", "RETURNED", "CANCELLED"], p=[0.87, 0.08, 0.05])
    if delay > 25 and status == "DELIVERED":
        if random.random() < 0.35:
            status = "RETURNED"

    o_time = order_timestamps[i]
    if status == "CANCELLED":
        d_time = None
        rating = None
        pg_fee = 0.0
    else:
        d_time = o_time + timedelta(minutes=actual_duration)
        pg_fee = round((line_gross - discount + del_fee) * 0.018, 2)
        if status == "RETURNED":
            rating = np.random.choice([1, 2], p=[0.7, 0.3])
        else:
            if delay == 0:
                rating = np.random.choice([4, 5], p=[0.3, 0.7])
            elif delay <= 10:
                rating = np.random.choice([3, 4], p=[0.5, 0.5])
            else:
                rating = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])

    gross_sales.append(line_gross)
    unit_costs_incurred.append(line_cost)
    promo_discounts.append(discount)
    delivery_fees_charged.append(del_fee)
    actual_delivery_costs.append(round(base_del_cost, 2))
    payment_gateway_fees.append(pg_fee)
    payment_methods.append(np.random.choice(payment_pool, p=payment_weights))
    order_statuses.append(status)
    delivered_timestamps.append(d_time)
    customer_ratings.append(rating)

df_orders = pd.DataFrame(
    {
        "order_id": order_ids,
        "customer_id": chosen_customers,
        "product_id": chosen_products,
        "hub_id": chosen_hubs,
        "order_timestamp": order_timestamps,
        "delivered_timestamp": delivered_timestamps,
        "order_status": order_statuses,
        "quantity": quantities,
        "gross_sales": gross_sales,
        "item_cost": unit_costs_incurred,
        "promo_discount": promo_discounts,
        "delivery_fee_charged": delivery_fees_charged,
        "actual_delivery_cost": actual_delivery_costs,
        "payment_gateway_fee": payment_gateway_fees,
        "payment_method": payment_methods,
        "sla_delay_minutes": sla_delay_minutes,
        "customer_rating": customer_ratings,
    }
)

# --- 5. Export to Excel ---
print(f"Saving workbook to {FILE_PATH}...")
with pd.ExcelWriter(FILE_PATH, engine="xlsxwriter") as writer:
    df_customers.to_excel(writer, sheet_name="dim_customers", index=False)
    df_darkstores.to_excel(writer, sheet_name="dim_darkstores", index=False)
    df_products.to_excel(writer, sheet_name="dim_products", index=False)
    df_orders.to_excel(writer, sheet_name="fact_orders", index=False)

print("Dataset generation complete.")
print(f"- Customers: {len(df_customers)}")
print(f"- Darkstores: {len(df_darkstores)}")
print(f"- Products: {len(df_products)}")
print(f"- Orders: {len(df_orders)}")