-- --- 1. Monthly Customer Cohort Retention ---
WITH customer_cohort_base AS (
    -- Initial cohort month per customer
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_timestamp)) AS cohort_month
    FROM raw_retail.fact_orders
    WHERE order_status = 'DELIVERED'
    GROUP BY customer_id
),
customer_activities AS (
    -- Subsequent activity months
    SELECT 
        o.customer_id,
        DATE_TRUNC('month', o.order_timestamp) AS order_month
    FROM raw_retail.fact_orders o
    WHERE o.order_status = 'DELIVERED'
    GROUP BY o.customer_id, DATE_TRUNC('month', o.order_timestamp)
),
cohort_index_mapping AS (
    -- Month index elapsed since first order (M0, M1, M2...)
    SELECT 
        b.cohort_month,
        a.order_month,
        (
            (EXTRACT(YEAR FROM a.order_month) - EXTRACT(YEAR FROM b.cohort_month)) * 12 +
            (EXTRACT(MONTH FROM a.order_month) - EXTRACT(MONTH FROM b.cohort_month))
        )::INT AS cohort_index,
        a.customer_id
    FROM customer_activities a
    JOIN customer_cohort_base b ON a.customer_id = b.customer_id
),
cohort_aggregations AS (
    -- Active customer counts per cohort bucket
    SELECT 
        cohort_month::DATE AS cohort,
        cohort_index,
        COUNT(DISTINCT customer_id) AS active_users
    FROM cohort_index_mapping
    GROUP BY cohort_month, cohort_index
)
SELECT 
    cohort,
    MAX(CASE WHEN cohort_index = 0 THEN active_users END) AS m0_base_size,
    ROUND(MAX(CASE WHEN cohort_index = 1 THEN active_users END)::NUMERIC / 
          NULLIF(MAX(CASE WHEN cohort_index = 0 THEN active_users END), 0) * 100, 1) AS m1_retention_pct,
    ROUND(MAX(CASE WHEN cohort_index = 2 THEN active_users END)::NUMERIC / 
          NULLIF(MAX(CASE WHEN cohort_index = 0 THEN active_users END), 0) * 100, 1) AS m2_retention_pct,
    ROUND(MAX(CASE WHEN cohort_index = 3 THEN active_users END)::NUMERIC / 
          NULLIF(MAX(CASE WHEN cohort_index = 0 THEN active_users END), 0) * 100, 1) AS m3_retention_pct,
    ROUND(MAX(CASE WHEN cohort_index = 4 THEN active_users END)::NUMERIC / 
          NULLIF(MAX(CASE WHEN cohort_index = 0 THEN active_users END), 0) * 100, 1) AS m4_retention_pct,
    ROUND(MAX(CASE WHEN cohort_index = 5 THEN active_users END)::NUMERIC / 
          NULLIF(MAX(CASE WHEN cohort_index = 0 THEN active_users END), 0) * 100, 1) AS m5_retention_pct
FROM cohort_aggregations
GROUP BY cohort
ORDER BY cohort;


-- --- 2. Darkstore Hub Unit Economics & SLA Ranking ---
WITH hub_performance_summary AS (
    SELECT 
        d.hub_id,
        d.hub_name,
        d.city,
        COUNT(o.order_id) AS total_orders,
        COUNT(o.order_id) FILTER (WHERE o.order_status = 'DELIVERED') AS delivered_orders,
        COUNT(o.order_id) FILTER (WHERE o.order_status = 'RETURNED') AS returned_orders,
        ROUND(AVG(o.sla_delay_treated) FILTER (WHERE o.order_status = 'DELIVERED'), 1) AS avg_delay_mins,
        SUM(o.net_sales) AS total_net_revenue,
        SUM(o.cm2_variable_profit) AS total_cm2_profit
    FROM raw_retail.dim_darkstores d
    LEFT JOIN raw_retail.fact_orders o ON d.hub_id = o.hub_id
    GROUP BY d.hub_id, d.hub_name, d.city
)
SELECT 
    hub_name,
    city,
    total_orders,
    ROUND((returned_orders::NUMERIC / NULLIF(total_orders, 0)) * 100, 2) AS return_rate_pct,
    avg_delay_mins,
    total_net_revenue,
    total_cm2_profit,
    ROUND((total_cm2_profit / NULLIF(total_net_revenue, 0)) * 100, 2) AS cm2_margin_pct,
    DENSE_RANK() OVER (ORDER BY total_cm2_profit DESC) AS national_profit_rank,
    DENSE_RANK() OVER (PARTITION BY city ORDER BY total_cm2_profit DESC) AS city_profit_rank,
    SUM(total_cm2_profit) OVER (
        ORDER BY total_cm2_profit DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_running_cm2
FROM hub_performance_summary
ORDER BY national_profit_rank;