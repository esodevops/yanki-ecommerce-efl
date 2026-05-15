from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    db_schema: str
    db_port: int
    raw_csv_path: Path
    clean_data_dir: Path


_REQUIRED_ENV = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")


def load_settings() -> Settings:
    load_dotenv(override=False)

    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Missing required environment variables: {missing_list}")

    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_schema = os.getenv("DB_SCHEMA", "yanki")
    db_port = int(os.getenv("DB_PORT", "5432"))

    raw_csv_path = Path(
        os.getenv("RAW_CSV_PATH", "dataset/rawdata/yanki_ecommerce.csv")
    )
    clean_data_dir = Path(os.getenv("CLEAN_DATA_DIR", "dataset/cleandata"))

    return Settings(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        db_schema=db_schema,
        db_port=db_port,
        raw_csv_path=raw_csv_path,
        clean_data_dir=clean_data_dir,
    )
