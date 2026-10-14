import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

PROCESSED_DIR = "data/processed"

print("=" * 70)
print("Statistical hypothesis testing and inferential analysis...")
print("=" * 70)

# Load cleaned facts and dimensions
df_orders = pd.read_csv(f"{PROCESSED_DIR}/fact_orders_clean.csv")
df_customers = pd.read_csv(f"{PROCESSED_DIR}/dim_customers_clean.csv")

# Join customer attributes for segment analysis
df_merged = df_orders.merge(df_customers, on="customer_id", how="inner")
delivered_orders = df_merged[df_merged["order_status"] == "DELIVERED"].copy()

# --- 1. Welch's t-test: Order Value by Loyalty Tier ---
print("\n[Hypothesis 1: Welch's Two-Sample Independent t-test]")
print("  H0: Mean Gross Sales of Premium Tiers (Gold/Platinum) == Entry Tiers (Bronze/Silver)")
print("  H1: Mean Gross Sales of Premium Tiers (Gold/Platinum) != Entry Tiers (Bronze/Silver)")

premium_spend = delivered_orders[delivered_orders["lifetime_rewards_tier"].isin(["Gold", "Platinum"])]["gross_sales"]
entry_spend = delivered_orders[delivered_orders["lifetime_rewards_tier"].isin(["Bronze", "Silver"])]["gross_sales"]

print(f"  - Sample Size (Premium): {len(premium_spend)} | Mean: ₹{premium_spend.mean():.2f} (Std: {premium_spend.std():.2f})")
print(f"  - Sample Size (Entry):   {len(entry_spend)} | Mean: ₹{entry_spend.mean():.2f} (Std: {entry_spend.std():.2f})")

# Run Welch's t-test with unequal variances
t_stat, p_val = stats.ttest_ind(premium_spend, entry_spend, equal_var=False)

print(f"\n  Results: t-statistic = {t_stat:.4f}, p-value = {p_val:.4e}")
alpha = 0.05
if p_val < alpha:
    print("  Decision: Reject H0 (p < 0.05)")
    print("  Conclusion: Statistically significant spend difference observed across loyalty tiers.")
else:
    print("  Decision: Fail to reject H0 (p >= 0.05)")
    print("  Conclusion: No statistically significant difference in spend across loyalty tiers.")

# --- 2. Chi-Square Test: SLA Delay vs. Doorstep Returns ---
print("\n" + "-" * 70)
print("[Hypothesis 2: Chi-Square Test of Independence]")
print("  H0: Order return status is independent of delivery SLA delay.")
print("  H1: Order return status is dependent on delivery SLA delay.")

# Filter out cancelled orders
completed_orders = df_orders[df_orders["order_status"].isin(["DELIVERED", "RETURNED"])].copy()
completed_orders["is_delayed"] = np.where(completed_orders["sla_delay_minutes"] > 15, "Severe Delay (>15m)", "On-Time / Mild")

contingency_table = pd.crosstab(completed_orders["is_delayed"], completed_orders["order_status"])
print("\n  Observed Contingency Table:")
print(contingency_table)

chi2, p_chi2, dof, expected = stats.chi2_contingency(contingency_table)

print(f"\n  Results: Chi2-statistic = {chi2:.4f}, p-value = {p_chi2:.4e}, Degrees of Freedom = {dof}")
if p_chi2 < alpha:
    print("  Decision: Reject H0 (p < 0.05)")
    print("  Conclusion: Fulfillment delays exceeding 15 minutes are significantly associated with customer returns.")
else:
    print("  Decision: Fail to reject H0 (p >= 0.05)")
    print("  Conclusion: Returns are independent of delivery delays.")

print("=" * 70)