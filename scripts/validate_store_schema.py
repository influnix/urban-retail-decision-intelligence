"""점포 데이터 연도별 헤더를 표준 스키마 계약으로 검증한다."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from mosaic.ingestion.schema_contract import (
    SchemaContractError,
    load_schema_contract,
    normalize_columns,
)
from mosaic.ingestion.text_profile import (
    create_header_signature,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROFILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "csv_profiles.csv"
)

CONTRACT_PATH = (
    PROJECT_ROOT
    / "configs"
    / "store_schema.toml"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "store_schema_report.csv"
)


def write_report(
    rows: list[dict[str, str | int]],
) -> None:
    """스키마 검증 결과를 CSV로 저장한다."""
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "year",
        "status",
        "source_column_count",
        "normalized_column_count",
        "source_header_signature",
        "normalized_header_signature",
        "error",
    ]

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """점포 CSV 프로파일 전체를 계약과 비교한다."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"CSV 프로파일이 없다: {PROFILE_PATH}"
        )

    contract = load_schema_contract(CONTRACT_PATH)
    report_rows: list[dict[str, str | int]] = []

    with PROFILE_PATH.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["dataset_type"] != "stores":
                continue

            source_headers = json.loads(
                row["headers_json"]
            )

            try:
                normalized_headers = normalize_columns(
                    source_headers,
                    contract,
                )

                status = "pass"
                error = ""
                normalized_signature = (
                    create_header_signature(
                        normalized_headers
                    )
                )

            except SchemaContractError as exc:
                status = "fail"
                error = str(exc)
                normalized_headers = []
                normalized_signature = ""

            report_rows.append(
                {
                    "year": row["year"],
                    "status": status,
                    "source_column_count": len(
                        source_headers
                    ),
                    "normalized_column_count": len(
                        normalized_headers
                    ),
                    "source_header_signature": row[
                        "header_signature"
                    ],
                    "normalized_header_signature": (
                        normalized_signature
                    ),
                    "error": error,
                }
            )

            print(
                f"[{status.upper()}] "
                f"{row['year']} | "
                f"source={len(source_headers)} | "
                f"normalized={len(normalized_headers)}"
            )

    if not report_rows:
        raise RuntimeError(
            "점포 데이터 프로파일을 찾지 못했다."
        )

    write_report(report_rows)

    failed_rows = [
        row
        for row in report_rows
        if row["status"] == "fail"
    ]

    normalized_signatures = {
        row["normalized_header_signature"]
        for row in report_rows
        if row["status"] == "pass"
    }

    print("-" * 70)
    print(f"검증 연도 수: {len(report_rows)}")
    print(f"실패 연도 수: {len(failed_rows)}")
    print(
        "표준화 후 헤더 서명 수: "
        f"{len(normalized_signatures)}"
    )
    print(f"결과 파일: {OUTPUT_PATH}")

    if failed_rows:
        raise RuntimeError(
            f"스키마 계약 실패: {len(failed_rows)}개"
        )

    if len(normalized_signatures) != 1:
        raise RuntimeError(
            "표준화 후에도 연도별 헤더가 일치하지 않는다."
        )


if __name__ == "__main__":
    main()