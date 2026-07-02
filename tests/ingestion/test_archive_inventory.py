"""ZIP 원천 파일 감사 기능 테스트."""

from pathlib import Path
from zipfile import ZipFile

from mosaic.ingestion.archive_inventory import inspect_archive


def test_inspect_archive_returns_member_information(tmp_path: Path) -> None:
    """ZIP 내부 파일의 이름과 크기를 반환해야 한다."""
    archive_path = tmp_path / "sample.zip"

    with ZipFile(archive_path, mode="w") as archive:
        archive.writestr("sample/data.csv", "a,b\n1,2\n")
        archive.writestr("sample/readme.txt", "테스트")

    result = inspect_archive(archive_path)

    assert result["archive_name"] == "sample.zip"
    assert result["archive_ok"] is True
    assert result["member_count"] == 2

    member_names = {member["member_name"] for member in result["members"]}

    assert "sample/data.csv" in member_names
    assert "sample/readme.txt" in member_names


def test_inspect_archive_detects_invalid_zip(tmp_path: Path) -> None:
    """잘못된 ZIP 파일은 정상 파일로 판정하면 안 된다."""
    archive_path = tmp_path / "invalid.zip"
    archive_path.write_text("이 파일은 ZIP이 아니다.", encoding="utf-8")

    result = inspect_archive(archive_path)

    assert result["archive_ok"] is False
    assert result["member_count"] == 0
    assert result["error"]