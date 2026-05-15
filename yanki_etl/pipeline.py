from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd
from psycopg2 import sql
from psycopg2.extras import execute_values

from yanki_etl.config import Settings
from yanki_etl.db import db_connection, ensure_database_exists
from yanki_etl.schema import build_schema_statements

LOGGER = logging.getLogger(__name__)


def _normalize_data(raw_csv_path: Path) -> dict[str, pd.DataFrame]:
    if not raw_csv_path.exists():
        raise FileNotFoundError(f"Raw CSV file not found: {raw_csv_path}")

    df = pd.read_csv(raw_csv_path)

    df = df.dropna(subset=["Order_ID", "Customer_ID"]).copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce").dt.date

    customers = (
        df[["Customer_ID", "Customer_Name", "Email", "Phone_Number"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    products = (
        df[["Product_ID", "Product_Name", "Brand", "Category", "Price"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    shipping_address = (
        df[
            [
                "Customer_ID",
                "Shipping_Address",
                "City",
                "State",
                "Country",
                "Postal_Code",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    shipping_address.index = shipping_address.index + 1
    shipping_address.index.name = "Shipping_ID"
    shipping_address = shipping_address.reset_index()
    shipping_address["Postal_Code"] = shipping_address["Postal_Code"].astype("string")

    orders = (
        df[
            [
                "Order_ID",
                "Customer_ID",
                "Product_ID",
                "Quantity",
                "Total_Price",
                "Order_Date",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    payment_method = (
        df[["Order_ID", "Payment_Method", "Transaction_Status"]]
        .drop_duplicates(subset=["Order_ID"])
        .reset_index(drop=True)
    )

    return {
        "customers": customers,
        "products": products,
        "shipping_address": shipping_address,
        "orders": orders,
        "payment_method": payment_method,
    }


def _write_clean_dataframes(
    clean_data_dir: Path, tables: dict[str, pd.DataFrame]
) -> None:
    clean_data_dir.mkdir(parents=True, exist_ok=True)
    for table_name, dataframe in tables.items():
        output_path = clean_data_dir / f"{table_name}.csv"
        dataframe.to_csv(output_path, index=False)
        LOGGER.info("Wrote cleaned data to %s", output_path)


def _run_schema_bootstrap(settings: Settings) -> None:
    with db_connection(settings) as conn:
        with conn.cursor() as cur:
            for statement in build_schema_statements(settings):
                cur.execute(statement)
        conn.commit()


def _read_csv_rows(csv_path: Path) -> Iterable[tuple]:
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            yield tuple(row)


def _load_table(
    settings: Settings,
    table_name: str,
    columns: list[str],
    conflict_columns: list[str],
    update_columns: list[str],
) -> None:
    csv_path = settings.clean_data_dir / f"{table_name}.csv"
    rows = list(_read_csv_rows(csv_path))
    if not rows:
        LOGGER.info("No rows found for %s, skipping load.", table_name)
        return

    schema_ident = sql.Identifier(settings.db_schema)
    table_ident = sql.Identifier(table_name)
    column_identifiers = [sql.Identifier(col) for col in columns]
    conflict_identifiers = [sql.Identifier(col) for col in conflict_columns]
    update_assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
        for col in update_columns
    ]

    insert_sql = sql.SQL(
        "INSERT INTO {}.{} ({}) VALUES %s ON CONFLICT ({}) DO UPDATE SET {};"
    ).format(
        schema_ident,
        table_ident,
        sql.SQL(", ").join(column_identifiers),
        sql.SQL(", ").join(conflict_identifiers),
        sql.SQL(", ").join(update_assignments),
    )

    with db_connection(settings) as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, rows, page_size=1000)
        conn.commit()

    LOGGER.info("Loaded %s rows into %s.%s", len(rows), settings.db_schema, table_name)


def run_pipeline(settings: Settings) -> None:
    LOGGER.info("Starting Yanki ETL pipeline")

    ensure_database_exists(settings)
    LOGGER.info("Verified database exists: %s", settings.db_name)

    normalized_tables = _normalize_data(settings.raw_csv_path)
    _write_clean_dataframes(settings.clean_data_dir, normalized_tables)

    _run_schema_bootstrap(settings)
    LOGGER.info("Schema bootstrap completed for schema: %s", settings.db_schema)

    _load_table(
        settings,
        table_name="customers",
        columns=["customer_id", "customer_name", "email", "phone_number"],
        conflict_columns=["customer_id"],
        update_columns=["customer_name", "email", "phone_number"],
    )
    _load_table(
        settings,
        table_name="products",
        columns=["product_id", "product_name", "brand", "category", "price"],
        conflict_columns=["product_id"],
        update_columns=["product_name", "brand", "category", "price"],
    )
    _load_table(
        settings,
        table_name="shipping_address",
        columns=[
            "shipping_id",
            "customer_id",
            "shipping_address",
            "city",
            "state",
            "country",
            "postal_code",
        ],
        conflict_columns=["shipping_id"],
        update_columns=[
            "customer_id",
            "shipping_address",
            "city",
            "state",
            "country",
            "postal_code",
        ],
    )
    _load_table(
        settings,
        table_name="orders",
        columns=[
            "order_id",
            "customer_id",
            "product_id",
            "quantity",
            "total_price",
            "order_date",
        ],
        conflict_columns=["order_id"],
        update_columns=[
            "customer_id",
            "product_id",
            "quantity",
            "total_price",
            "order_date",
        ],
    )
    _load_table(
        settings,
        table_name="payment_method",
        columns=["order_id", "payment_method", "transaction_status"],
        conflict_columns=["order_id"],
        update_columns=["payment_method", "transaction_status"],
    )

    LOGGER.info("Yanki ETL pipeline completed successfully")
