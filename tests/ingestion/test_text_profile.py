"""ZIP 내부 CSV 프로파일링 기능 테스트."""

from __future__ import annotations

import codecs
from pathlib import Path
from zipfile import ZipFile

from mosaic.ingestion.text_profile import inspect_csv_members


def test_inspect_csv_members_detects_cp949(tmp_path: Path) -> None:
    """CP949 CSV의 인코딩과 헤더를 확인해야 한다."""
    archive_path = tmp_path / "sales.zip"
    content = "기준_년_코드,매출액\n2025,1000\n".encode("cp949")

    with ZipFile(archive_path, mode="w") as archive:
        archive.writestr("sales.csv", content)

    result = inspect_csv_members(archive_path)

    assert len(result) == 1
    assert result[0]["encoding"] == "cp949"
    assert result[0]["delimiter"] == ","
    assert result[0]["column_count"] == 2
    assert result[0]["headers"] == ["기준_년_코드", "매출액"]
    assert result[0]["error"] == ""


def test_inspect_csv_members_detects_utf8_bom_and_tab(
    tmp_path: Path,
) -> None:
    """UTF-8 BOM과 탭 구분자를 확인해야 한다."""
    archive_path = tmp_path / "stores.zip"

    text = "상권_코드\t점포_수\n1001\t5\n"
    content = codecs.BOM_UTF8 + text.encode("utf-8")

    with ZipFile(archive_path, mode="w") as archive:
        archive.writestr("stores.csv", content)

    result = inspect_csv_members(archive_path)

    assert len(result) == 1
    assert result[0]["encoding"] == "utf-8-sig"
    assert result[0]["delimiter"] == "\t"
    assert result[0]["column_count"] == 2
    assert result[0]["headers"] == ["상권_코드", "점포_수"]


def test_inspect_csv_members_returns_empty_for_non_csv_archive(
    tmp_path: Path,
) -> None:
    """CSV가 없는 ZIP에는 빈 목록을 반환해야 한다."""
    archive_path = tmp_path / "areas.zip"

    with ZipFile(archive_path, mode="w") as archive:
        archive.writestr("areas.shp", b"sample")

    result = inspect_csv_members(archive_path)

    assert result == []