from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection

from yanki_etl.config import Settings


@contextmanager
def db_connection(
    settings: Settings, database: str | None = None
) -> Generator[PgConnection, None, None]:
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=database or settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    try:
        yield conn
    finally:
        conn.close()


def ensure_database_exists(settings: Settings) -> None:
    with db_connection(settings, database="postgres") as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (settings.db_name,),
            )
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE DATABASE {};").format(
                        sql.Identifier(settings.db_name)
                    )
                )
