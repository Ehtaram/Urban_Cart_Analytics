-- Schemas and Extensions
CREATE SCHEMA IF NOT EXISTS raw_retail;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables (reverse dependency order)
DROP TABLE IF EXISTS raw_retail.fact_orders;
DROP TABLE IF EXISTS raw_retail.dim_products;
DROP TABLE IF EXISTS raw_retail.dim_darkstores;
DROP TABLE IF EXISTS raw_retail.dim_customers;

-- --- 1. Customer Dimension ---
CREATE TABLE raw_retail.dim_customers (
    customer_id             VARCHAR(20) NOT NULL,
    signup_date             TIMESTAMPTZ NOT NULL,
    customer_segment        VARCHAR(50) NOT NULL,
    city_tier               VARCHAR(30) NOT NULL,
    lifetime_rewards_tier   VARCHAR(20) NOT NULL,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT pk_dim_customers PRIMARY KEY (customer_id),
    CONSTRAINT chk_rewards_tier CHECK (
        lifetime_rewards_tier IN ('Bronze', 'Silver', 'Gold', 'Platinum')
    )
);

-- --- 2. Darkstore Dimension ---
CREATE TABLE raw_retail.dim_darkstores (
    hub_id                  VARCHAR(20) NOT NULL,
    hub_name                VARCHAR(100) NOT NULL,
    city                    VARCHAR(50) NOT NULL,
    daily_operating_cost    NUMERIC(12, 2) NOT NULL,
    target_sla_minutes      INT NOT NULL,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT pk_dim_darkstores PRIMARY KEY (hub_id),
    CONSTRAINT chk_daily_cost_positive CHECK (daily_operating_cost >= 0.00),
    CONSTRAINT chk_target_sla_positive CHECK (target_sla_minutes > 0)
);

-- --- 3. Product Dimension ---
CREATE TABLE raw_retail.dim_products (
    product_id              VARCHAR(20) NOT NULL,
    product_name            VARCHAR(150) NOT NULL,
    category                VARCHAR(60) NOT NULL,
    unit_cost               NUMERIC(10, 2) NOT NULL,
    listing_price           NUMERIC(10, 2) NOT NULL,
    created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT pk_dim_products PRIMARY KEY (product_id),
    CONSTRAINT chk_product_costs CHECK (unit_cost >= 0.00 AND listing_price >= 0.00)
);

-- --- 4. Fact Orders ---
CREATE TABLE raw_retail.fact_orders (
    order_id                VARCHAR(30) NOT NULL,
    customer_id             VARCHAR(20) NOT NULL,
    product_id              VARCHAR(20) NOT NULL,
    hub_id                  VARCHAR(20) NOT NULL,
    order_timestamp         TIMESTAMPTZ NOT NULL,
    delivered_timestamp     TIMESTAMPTZ,
    order_status            VARCHAR(20) NOT NULL,
    quantity                INT NOT NULL,
    gross_sales             NUMERIC(12, 2) NOT NULL,
    item_cost               NUMERIC(12, 2) NOT NULL,
    promo_discount          NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    delivery_fee_charged    NUMERIC(8, 2) DEFAULT 0.00 NOT NULL,
    actual_delivery_cost    NUMERIC(8, 2) NOT NULL,
    payment_gateway_fee     NUMERIC(8, 2) DEFAULT 0.00 NOT NULL,
    payment_method          VARCHAR(30) NOT NULL,
    sla_delay_minutes       INT DEFAULT 0 NOT NULL,
    customer_rating         INT,
    sla_delay_treated       NUMERIC(6, 2) NOT NULL,
    net_sales               NUMERIC(12, 2) NOT NULL,
    cm1_gross_margin        NUMERIC(12, 2) NOT NULL,
    net_logistics_balance   NUMERIC(10, 2) NOT NULL,
    cm2_variable_profit     NUMERIC(12, 2) NOT NULL,
    cm2_margin_pct          NUMERIC(6, 2) NOT NULL,
    is_profitable           INT NOT NULL,
    
    -- Table Constraints
    CONSTRAINT pk_fact_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES raw_retail.dim_customers (customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id) 
        REFERENCES raw_retail.dim_products (product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_hub FOREIGN KEY (hub_id) 
        REFERENCES raw_retail.dim_darkstores (hub_id) ON DELETE RESTRICT,
    CONSTRAINT chk_order_status CHECK (
        order_status IN ('DELIVERED', 'RETURNED', 'CANCELLED')
    ),
    CONSTRAINT chk_rating_range CHECK (
        customer_rating IS NULL OR (customer_rating >= 1 AND customer_rating <= 5)
    )
);

-- --- Indexes ---
CREATE INDEX idx_orders_customer_id ON raw_retail.fact_orders (customer_id);
CREATE INDEX idx_orders_product_id  ON raw_retail.fact_orders (product_id);
CREATE INDEX idx_orders_hub_id      ON raw_retail.fact_orders (hub_id);
CREATE INDEX idx_orders_timestamp   ON raw_retail.fact_orders (order_timestamp);
CREATE INDEX idx_orders_status      ON raw_retail.fact_orders (order_status);