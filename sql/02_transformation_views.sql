-- Materialized view for Power BI reporting layer
CREATE MATERIALIZED VIEW analytics.mv_daily_hub_unit_economics AS
SELECT 
    DATE_TRUNC('day', o.order_timestamp)::DATE AS order_date,
    o.hub_id,
    d.hub_name,
    d.city,
    p.category AS product_category,
    o.payment_method,
    COUNT(o.order_id) AS order_volume,
    SUM(o.quantity) AS units_sold,
    SUM(o.gross_sales) AS total_gross_sales,
    SUM(o.promo_discount) AS total_promo_burn,
    SUM(o.net_sales) AS total_net_sales,
    SUM(o.item_cost) AS total_cogs,
    SUM(o.cm1_gross_margin) AS total_cm1_margin,
    SUM(o.delivery_fee_charged) AS total_delivery_fees_collected,
    SUM(o.actual_delivery_cost) AS total_logistics_fleet_cost,
    SUM(o.net_logistics_balance) AS total_logistics_burn,
    SUM(o.payment_gateway_fee) AS total_pg_fees,
    SUM(o.cm2_variable_profit) AS total_cm2_profit,
    COUNT(o.order_id) FILTER (WHERE o.order_status = 'RETURNED') AS return_volume,
    COUNT(o.order_id) FILTER (WHERE o.sla_delay_minutes > 15) AS severe_delay_volume
FROM raw_retail.fact_orders o
JOIN raw_retail.dim_darkstores d ON o.hub_id = d.hub_id
JOIN raw_retail.dim_products p   ON o.product_id = p.product_id
GROUP BY 
    DATE_TRUNC('day', o.order_timestamp)::DATE,
    o.hub_id,
    d.hub_name,
    d.city,
    p.category,
    o.payment_method
WITH DATA;

-- Unique index to support concurrent refresh
CREATE UNIQUE INDEX idx_mv_daily_hub ON analytics.mv_daily_hub_unit_economics (order_date, hub_id, product_category, payment_method);