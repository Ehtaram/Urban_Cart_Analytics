import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

# Database Configuration
DB_CONFIG = {
    "dbname": "urbancart_dw",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": 5432
}

PROCESSED_DIR = "data/processed"
DDL_FILE = "sql/01_schema_ddl.sql"

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as err:
        print(f"Database Connection Error: {err}")
        raise

def initialize_schema(conn):
    print("Executing Schema DDL in urbancart_dw...")
    with conn.cursor() as cur:
        with open(DDL_FILE, "r") as f:
            ddl_queries = f.read()
        cur.execute(ddl_queries)
    conn.commit()
    print("Schema DDL applied successfully.")

def ingest_dataframe(conn, df, table_name, schema="raw_retail"):
    cursor = conn.cursor()
    cols = ",".join(list(df.columns))
    query = f"INSERT INTO {schema}.{table_name} ({cols}) VALUES %s"
    
    # Replacing NaN with None so psycopg2 inserts SQL NULL
    records = df.replace({pd.NA: None, float("nan"): None}).values.tolist()
    
    print(f"Loading {len(records)} rows into {schema}.{table_name}...")
    execute_values(cursor, query, records, page_size=1000)
    conn.commit()
    cursor.close()
    print(f"{table_name} populated.")

def main():
    print("=" * 70)
    print("Starting PostgreSQL batch ingestion...")
    print("=" * 70)
    
    conn = connect_db()
    
    # 1. Initialize DB structure
    #initialize_schema(conn)
    
    # 2. Ingest Dimension Tables First (Parent records)
    df_customers = pd.read_csv(f"{PROCESSED_DIR}/dim_customers_clean.csv")
    df_darkstores = pd.read_csv(f"{PROCESSED_DIR}/dim_darkstores_clean.csv")
    df_products = pd.read_csv(f"{PROCESSED_DIR}/dim_products_clean.csv")
    
    ingest_dataframe(conn, df_customers, "dim_customers")
    ingest_dataframe(conn, df_darkstores, "dim_darkstores")
    ingest_dataframe(conn, df_products, "dim_products")
    
    # 3. Ingest Fact Orders (Child records)
    df_orders = pd.read_csv(f"{PROCESSED_DIR}/fact_orders_clean.csv")
    ingest_dataframe(conn, df_orders, "fact_orders")
    
    # 4. Ingestion Sanity Verification
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM raw_retail.dim_customers)  AS cust_count,
                (SELECT COUNT(*) FROM raw_retail.dim_darkstores) AS hub_count,
                (SELECT COUNT(*) FROM raw_retail.dim_products)   AS prod_count,
                (SELECT COUNT(*) FROM raw_retail.fact_orders)    AS order_count;
        """)
        counts = cur.fetchone()
        print("\nVerification Row Counts:")
        print(f"    - dim_customers:  {counts[0]} rows")
        print(f"    - dim_darkstores: {counts[1]} rows")
        print(f"    - dim_products:   {counts[2]} rows")
        print(f"    - fact_orders:    {counts[3]} rows")
    
    conn.close()
    print("=" * 70)
    print("Database load and verification complete.")
    print("=" * 70)

if __name__ == "__main__":
    main()