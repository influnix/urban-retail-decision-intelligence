"""ZIP 원천 파일의 내부 구조를 조사한다."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


def inspect_archive(archive_path: Path) -> dict[str, Any]:
    """ZIP 파일의 유효성과 내부 파일 목록을 반환한다."""
    try:
        with ZipFile(
            archive_path,
            metadata_encoding="cp949") as archive:
            corrupted_member = archive.testzip()

            members = [
                {
                    "member_name": info.filename,
                    "suffix": Path(info.filename).suffix.lower(),
                    "size_bytes": info.file_size,
                    "compressed_size_bytes": info.compress_size,
                    "is_directory": info.is_dir(),
                }
                for info in archive.infolist()
                if not info.is_dir()
            ]

            archive_ok = corrupted_member is None
            error = (
                ""
                if archive_ok
                else f"CRC 검사에 실패한 내부 파일: {corrupted_member}"
            )

            return {
                "archive_name": archive_path.name,
                "archive_path": str(archive_path),
                "archive_ok": archive_ok,
                "member_count": len(members),
                "members": members,
                "error": error,
            }

    except (BadZipFile, OSError) as exc:
        return {
            "archive_name": archive_path.name,
            "archive_path": str(archive_path),
            "archive_ok": False,
            "member_count": 0,
            "members": [],
            "error": str(exc),
        }