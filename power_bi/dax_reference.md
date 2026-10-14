# UrbanCart DAX Measures Reference Library

This document outlines all explicit Data Analysis Expressions (DAX) business metrics implemented in the Star-Schema Semantic Model.

---

## 1. Core Revenue & Volume Measures

### Total Orders:
Counts every transaction row in the fact table to serve as the baseline volume denominator.
```dax
Total Orders = 
COUNTROWS('raw_retail fact_orders')
```

### Delivered Orders:
Filters orders to only successful deliveries, excluding cancellations and returns for accurate fulfillment metrics.
```dax
Delivered Orders = 
CALCULATE(
    [Total Orders],
    KEEPFILTERS('raw_retail fact_orders'[order_status] = "DELIVERED")
)
```

### Gross Merchandise Value:
Calculates total gross sales value before any promo deductions or cancellations.
```dax
Gross Merchandise Value = 
SUM('raw_retail fact_orders'[gross_sales])
```

### Promo Discounts Burned:
Aggregates total promotional discounts given away to quantify top-line margin burn.
```dax
Promo Discounts Burned = 
SUM('raw_retail fact_orders'[promo_discount])
```

### Net Revenue:
Computes actual collected product revenue by subtracting promotional discounts from gross sales.
```dax
Net Revenue = 
SUM('raw_retail fact_orders'[net_sales])
```

### Average Order Value:
Measures the average basket spend per delivered order using safe division to avoid zero errors.
```dax
Average Order Value = 
DIVIDE([Net Revenue], [Delivered Orders], 0)
```

---

## 2. Unit Economics & Contribution Margins

### Total Direct COGS:
Sums the baseline supplier wholesale costs for all sold units to calculate merchandise expenditure.
```dax
Total Direct COGS = 
SUM('raw_retail fact_orders'[item_cost])
```

### CM1 Gross Profit:
Measures product-level gross margin by deducting wholesale inventory costs directly from net revenue.
```dax
CM1 Gross Profit = 
SUM('raw_retail fact_orders'[cm1_gross_margin])
```

### CM1 Margin %:
Evaluates base product markup strength as an exact percentage of net revenue.
```dax
CM1 Margin % = 
DIVIDE([CM1 Gross Profit], [Net Revenue], 0)
```

### Total Fleet Logistics Cost:
Aggregates true rider payouts and delivery fleet expenses incurred by the dark stores.
```dax
Total Fleet Logistics Cost = 
SUM('raw_retail fact_orders'[actual_delivery_cost])
```

### Total Delivery Fees Collected:
Totals the delivery fees charged directly to customers on sub-threshold orders.
```dax
Total Delivery Fees Collected = 
SUM('raw_retail fact_orders'[delivery_fee_charged])
```

### Logistics Deficit:
Quantifies fulfillment subsidy bleed by subtracting actual fleet expenses from customer delivery collections.
```dax
Logistics Deficit = 
[Total Delivery Fees Collected] - [Total Fleet Logistics Cost]
```

### CM2 Variable Contribution:
Calculates order-level operational profitability by factoring in product margin, logistics deficit, and payment gateway fees.
```dax
CM2 Variable Contribution = 
SUM('raw_retail fact_orders'[cm2_variable_profit])
```

### CM2 Margin %:
Expresses net variable operating profit as a percentage of net revenue to track platform viability.
```dax
CM2 Margin % = 
DIVIDE([CM2 Variable Contribution], [Net Revenue], 0)
```

### Profitable Orders Count:
Counts the number of delivered orders where CM2 contribution margin was strictly positive.
```dax
Profitable Orders Count = 
CALCULATE(
    [Total Orders],
    'raw_retail fact_orders'[is_profitable] = 1,
    'raw_retail fact_orders'[order_status] = "DELIVERED"
)
```

### Profitable Order Ratio:
Determines the percentage of completed orders that generate positive variable contribution.
```dax
Profitable Order Ratio = 
DIVIDE([Profitable Orders Count], [Delivered Orders], 0)
```

---

## 3. SLA Breaches & Operational Risk

### Returned Orders Count:
Isolates total customer-returned orders to evaluate post-delivery dissatisfaction.
```dax
Returned Orders Count = 
CALCULATE(
    [Total Orders],
    KEEPFILTERS('raw_retail fact_orders'[order_status] = "RETURNED")
)
```

### Return Rate %:
Calculates returns as a proportion of total orders to identify quality and delivery failure rates.
```dax
Return Rate % = 
DIVIDE([Returned Orders Count], [Total Orders], 0)
```

### SLA Breach Volume (>15m):
Filters for orders delayed by more than 15 minutes beyond their targeted dark-store delivery SLA.
```dax
SLA Breach Volume (>15m) = 
CALCULATE(
    [Total Orders],
    'raw_retail fact_orders'[sla_delay_minutes] > 15,
    'raw_retail fact_orders'[order_status] IN {"DELIVERED", "RETURNED"}
)
```

### SLA Breach Rate %:
Measures the percentage of completed orders that experienced severe delivery delays.
```dax
SLA Breach Rate % = 
VAR CompletedOrders = 
    CALCULATE(
        [Total Orders],
        'raw_retail fact_orders'[order_status] IN {"DELIVERED", "RETURNED"}
    )
RETURN
    DIVIDE([SLA Breach Volume (>15m)], CompletedOrders, 0)
```

---

## 4. Advanced Time-Intelligence & Rolling Retention DAX

### Net Revenue (Prior Month - PM):
Shifts the evaluation filter context back by exactly one month along the custom calendar dimension.
```dax
Net Revenue (Prior Month - PM) = 
CALCULATE(
    [Net Revenue],
    DATEADD('dim_date'[Date], -1, MONTH)
)
```

### Revenue MoM Growth %:
Computes Month-over-Month percentage revenue expansion or contraction relative to the previous month.
```dax
Revenue MoM Growth % = 
VAR CurrentRev = [Net Revenue]
VAR PrevRev = [Net Revenue (Prior Month - PM)]
RETURN
    DIVIDE(CurrentRev - PrevRev, PrevRev, 0)
```

### Rolling 30-Day CM2 Profit:
Calculates cumulative CM2 variable profit over a trailing 30-day window relative to the active date context.
```dax
Rolling 30-Day CM2 Profit = 
CALCULATE(
    [CM2 Variable Contribution],
    DATESINPERIOD('dim_date'[Date], MAX('dim_date'[Date]), -30, DAY)
)
```

### Cumulative YTD CM2:
Accumulates year-to-date variable contribution margin starting fresh on January 1st of each calendar year.
```dax
Cumulative YTD CM2 = 
TOTALYTD([CM2 Variable Contribution], 'dim_date'[Date])
```

### Total Payment Gateway Fees:
```dax
Total Payment Gateway Fees = 
SUM('raw_retail fact_orders'[payment_gateway_fee])
```