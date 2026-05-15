from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from yanki_etl.config import load_settings
from yanki_etl.logging_config import setup_logging
from yanki_etl.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Yanki production ETL pipeline")
    parser.add_argument(
        "--raw-csv",
        dest="raw_csv",
        default=None,
        help="Optional override path for raw CSV file",
    )
    parser.add_argument(
        "--clean-dir",
        dest="clean_dir",
        default=None,
        help="Optional override directory for cleaned CSV outputs",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    settings = load_settings()

    if args.raw_csv:
        settings = replace(settings, raw_csv_path=Path(args.raw_csv))
    if args.clean_dir:
        settings = replace(settings, clean_data_dir=Path(args.clean_dir))

    run_pipeline(settings)


if __name__ == "__main__":
    main()
