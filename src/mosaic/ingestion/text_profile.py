"""ZIP 내부 CSV의 인코딩과 헤더 구조를 조사한다."""

from __future__ import annotations

import codecs
import csv
import hashlib
import io
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

ZIP_METADATA_ENCODING = "cp949"
TEXT_ENCODING_CANDIDATES = ("utf-8", "cp949", "euc-kr")
DELIMITER_CANDIDATES = ",\t;|"


def decode_text_sample(raw: bytes) -> tuple[str, str]:
    """바이트 샘플을 디코딩할 수 있는 문자 인코딩을 찾는다."""
    candidates = list(TEXT_ENCODING_CANDIDATES)

    if raw.startswith(codecs.BOM_UTF8):
        candidates.insert(0, "utf-8-sig")

    for encoding in candidates:
        decoder = codecs.getincrementaldecoder(encoding)(
            errors="strict",
        )

        try:
            text = decoder.decode(raw, final=False)
        except UnicodeDecodeError:
            continue

        return encoding, text

    return "unknown", ""


def detect_delimiter(text: str) -> str:
    """CSV 텍스트 샘플에서 구분자를 추정한다."""
    non_empty_lines = [
        line
        for line in text.splitlines()[:20]
        if line.strip()
    ]

    if not non_empty_lines:
        return ""

    sample = "\n".join(non_empty_lines)

    try:
        dialect = csv.Sniffer().sniff(
            sample,
            delimiters=DELIMITER_CANDIDATES,
        )
        return dialect.delimiter
    except csv.Error:
        first_line = non_empty_lines[0]

        delimiter_counts = {
            delimiter: first_line.count(delimiter)
            for delimiter in DELIMITER_CANDIDATES
        }

        delimiter = max(
            delimiter_counts,
            key=delimiter_counts.get,
        )

        if delimiter_counts[delimiter] == 0:
            return ""

        return delimiter


def parse_header(text: str, delimiter: str) -> list[str]:
    """첫 번째 비어 있지 않은 CSV 행을 헤더로 반환한다."""
    if not delimiter:
        return []

    reader = csv.reader(
        io.StringIO(text),
        delimiter=delimiter,
    )

    for row in reader:
        cleaned_row = [value.strip() for value in row]

        if any(cleaned_row):
            return cleaned_row

    return []


def create_header_signature(headers: list[str]) -> str:
    """컬럼 목록 비교에 사용할 SHA-256 서명을 생성한다."""
    joined_headers = "\x1f".join(headers)

    return hashlib.sha256(
        joined_headers.encode("utf-8"),
    ).hexdigest()


def inspect_csv_members(
    archive_path: Path,
    sample_bytes: int = 131_072,
) -> list[dict[str, Any]]:
    """ZIP 내부 CSV 파일의 인코딩과 헤더를 조사한다."""
    profiles: list[dict[str, Any]] = []

    try:
        with ZipFile(
            archive_path,
            metadata_encoding=ZIP_METADATA_ENCODING,
        ) as archive:
            csv_members = [
                info
                for info in archive.infolist()
                if Path(info.filename).suffix.lower() == ".csv"
            ]

            for info in csv_members:
                with archive.open(info) as member_file:
                    raw = member_file.read(sample_bytes)

                encoding, text = decode_text_sample(raw)

                if encoding == "unknown":
                    profiles.append(
                        {
                            "archive_name": archive_path.name,
                            "member_name": info.filename,
                            "encoding": encoding,
                            "delimiter": "",
                            "column_count": 0,
                            "headers": [],
                            "header_signature": "",
                            "error": "문자 인코딩을 확인하지 못했다.",
                        }
                    )
                    continue

                delimiter = detect_delimiter(text)
                headers = parse_header(text, delimiter)

                error = ""

                if not delimiter:
                    error = "CSV 구분자를 확인하지 못했다."
                elif not headers:
                    error = "CSV 헤더를 확인하지 못했다."

                profiles.append(
                    {
                        "archive_name": archive_path.name,
                        "member_name": info.filename,
                        "encoding": encoding,
                        "delimiter": delimiter,
                        "column_count": len(headers),
                        "headers": headers,
                        "header_signature": (
                            create_header_signature(headers)
                            if headers
                            else ""
                        ),
                        "error": error,
                    }
                )

    except (BadZipFile, OSError) as exc:
        profiles.append(
            {
                "archive_name": archive_path.name,
                "member_name": "",
                "encoding": "unknown",
                "delimiter": "",
                "column_count": 0,
                "headers": [],
                "header_signature": "",
                "error": str(exc),
            }
        )

    return profiles