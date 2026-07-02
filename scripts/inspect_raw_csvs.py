"""원천 ZIP 내부 CSV의 인코딩과 헤더 구조를 조사한다."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from mosaic.ingestion.text_profile import inspect_csv_members

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "csv_profiles.csv"
)


def extract_year(archive_name: str) -> str:
    """압축 파일명에서 네 자리 연도를 추출한다."""
    match = re.search(r"20\d{2}", archive_name)

    return match.group(0) if match else ""


def classify_dataset(archive_name: str) -> str:
    """압축 파일명을 이용해 데이터셋 유형을 분류한다."""
    if "estimated_sales" in archive_name:
        return "sales"

    if "stores" in archive_name:
        return "stores"

    return "unknown"


def display_delimiter(delimiter: str) -> str:
    """탭 문자를 CSV에서 읽을 수 있는 문자열로 변환한다."""
    if delimiter == "\t":
        return "\\t"

    return delimiter


def create_output_row(
    archive_path: Path,
    profile: dict[str, Any],
) -> dict[str, Any]:
    """프로파일 결과를 CSV 저장용 행으로 변환한다."""
    return {
        "dataset_type": classify_dataset(archive_path.name),
        "year": extract_year(archive_path.name),
        "archive_name": profile["archive_name"],
        "member_name": profile["member_name"],
        "encoding": profile["encoding"],
        "delimiter": display_delimiter(profile["delimiter"]),
        "column_count": profile["column_count"],
        "header_signature": profile["header_signature"],
        "headers_json": json.dumps(
            profile["headers"],
            ensure_ascii=False,
        ),
        "error": profile["error"],
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    """CSV 프로파일 결과를 저장한다."""
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "dataset_type",
        "year",
        "archive_name",
        "member_name",
        "encoding",
        "delimiter",
        "column_count",
        "header_signature",
        "headers_json",
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
    """모든 원천 ZIP 내부의 CSV를 조사한다."""
    archive_paths = sorted(RAW_ROOT.rglob("*.zip"))
    rows: list[dict[str, Any]] = []

    for archive_path in archive_paths:
        profiles = inspect_csv_members(archive_path)

        for profile in profiles:
            row = create_output_row(
                archive_path,
                profile,
            )
            rows.append(row)

            delimiter = row["delimiter"] or "확인 실패"
            error = row["error"] or "없음"

            print(
                f"[{row['dataset_type']}] "
                f"{row['year']} | "
                f"encoding={row['encoding']} | "
                f"delimiter={delimiter} | "
                f"columns={row['column_count']} | "
                f"error={error}"
            )

    if not rows:
        raise RuntimeError(
            "ZIP 내부에서 CSV 파일을 찾지 못했다."
        )

    write_csv(rows)

    failed_rows = [
        row
        for row in rows
        if row["error"]
    ]

    print("-" * 70)
    print(f"조사한 CSV 수: {len(rows)}")
    print(f"오류 CSV 수: {len(failed_rows)}")
    print(f"결과 파일: {OUTPUT_PATH}")

    if failed_rows:
        raise RuntimeError(
            f"프로파일링에 실패한 CSV가 있다: "
            f"{len(failed_rows)}개"
        )


if __name__ == "__main__":
    main()