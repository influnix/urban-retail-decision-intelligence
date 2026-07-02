"""모든 원천 ZIP 파일의 내부 구조를 조사한다."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from mosaic.ingestion.archive_inventory import inspect_archive

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "data" / "metadata" / "archive_inventory.csv"


def flatten_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    """ZIP 단위 결과를 내부 파일 단위 행으로 변환한다."""
    if not result["members"]:
        return [
            {
                "archive_name": result["archive_name"],
                "archive_ok": result["archive_ok"],
                "member_count": result["member_count"],
                "member_name": "",
                "suffix": "",
                "size_bytes": "",
                "compressed_size_bytes": "",
                "error": result["error"],
            }
        ]

    return [
        {
            "archive_name": result["archive_name"],
            "archive_ok": result["archive_ok"],
            "member_count": result["member_count"],
            "member_name": member["member_name"],
            "suffix": member["suffix"],
            "size_bytes": member["size_bytes"],
            "compressed_size_bytes": member["compressed_size_bytes"],
            "error": result["error"],
        }
        for member in result["members"]
    ]


def write_csv(rows: list[dict[str, Any]]) -> None:
    """감사 결과를 CSV 파일로 저장한다."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "archive_name",
        "archive_ok",
        "member_count",
        "member_name",
        "suffix",
        "size_bytes",
        "compressed_size_bytes",
        "error",
    ]

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """원천 ZIP 전체를 조사하고 결과를 출력한다."""
    archive_paths = sorted(RAW_ROOT.rglob("*.zip"))

    if not archive_paths:
        raise FileNotFoundError(f"ZIP 파일을 찾지 못했다: {RAW_ROOT}")

    rows: list[dict[str, Any]] = []
    invalid_archives: list[str] = []

    for archive_path in archive_paths:
        result = inspect_archive(archive_path)
        rows.extend(flatten_result(result))

        status = "정상" if result["archive_ok"] else "오류"
        print(
            f"[{status}] {archive_path.name}: "
            f"{result['member_count']}개 내부 파일"
        )

        if not result["archive_ok"]:
            invalid_archives.append(archive_path.name)

    write_csv(rows)

    print("-" * 60)
    print(f"조사한 ZIP 수: {len(archive_paths)}")
    print(f"오류 ZIP 수: {len(invalid_archives)}")
    print(f"결과 파일: {OUTPUT_PATH}")

    if invalid_archives:
        raise RuntimeError(
            f"손상되거나 읽을 수 없는 ZIP이 있다: {invalid_archives}"
        )


if __name__ == "__main__":
    main()