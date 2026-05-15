from __future__ import annotations

from psycopg2 import sql

from yanki_etl.config import Settings


def build_schema_statements(settings: Settings) -> list[sql.Composed]:
    schema_ident = sql.Identifier(settings.db_schema)

    return [
        sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(schema_ident),
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.customers (
                customer_id UUID PRIMARY KEY,
                customer_name TEXT,
                email TEXT,
                phone_number TEXT
            );
            """).format(schema_ident),
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.products (
                product_id UUID PRIMARY KEY,
                product_name TEXT,
                brand TEXT,
                category TEXT,
                price NUMERIC(12,2)
            );
            """).format(schema_ident),
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.shipping_address (
                shipping_id INTEGER PRIMARY KEY,
                customer_id UUID REFERENCES {}.customers(customer_id),
                shipping_address TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                postal_code TEXT
            );
            """).format(schema_ident, schema_ident),
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.orders (
                order_id UUID PRIMARY KEY,
                customer_id UUID REFERENCES {}.customers(customer_id),
                product_id UUID REFERENCES {}.products(product_id),
                quantity INTEGER,
                total_price NUMERIC(12,2),
                order_date DATE
            );
            """).format(schema_ident, schema_ident, schema_ident),
        sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.payment_method (
                order_id UUID PRIMARY KEY REFERENCES {}.orders(order_id),
                payment_method TEXT,
                transaction_status TEXT
            );
            """).format(schema_ident, schema_ident),
        sql.SQL(
            "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON {}.orders(customer_id);"
        ).format(schema_ident),
        sql.SQL(
            "CREATE INDEX IF NOT EXISTS idx_orders_product_id ON {}.orders(product_id);"
        ).format(schema_ident),
        sql.SQL(
            "CREATE INDEX IF NOT EXISTS idx_orders_order_date ON {}.orders(order_date);"
        ).format(schema_ident),
    ]
