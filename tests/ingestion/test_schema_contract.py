"""점포 데이터 스키마 계약 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from mosaic.ingestion.schema_contract import (
    SchemaContract,
    SchemaContractError,
    load_schema_contract,
    normalize_columns,
)

CANONICAL_COLUMNS = (
    "year_quarter_code",
    "commercial_area_type_code",
    "commercial_area_type_name",
    "commercial_area_code",
    "commercial_area_name",
    "service_industry_code",
    "service_industry_name",
    "store_count",
    "similar_industry_store_count",
    "opening_rate",
    "opening_store_count",
    "closure_rate",
    "closure_store_count",
    "franchise_store_count",
)


def make_contract() -> SchemaContract:
    """테스트용 점포 스키마 계약을 만든다."""
    return SchemaContract(
        dataset="stores",
        canonical_columns=CANONICAL_COLUMNS,
        aliases={
            "기준_년분기_코드": "year_quarter_code",
            "점포_수": "store_count",
            "stdr_yyqu_cd": "year_quarter_code",
            "stor_co": "store_count",
        },
    )


def test_normalize_columns_maps_korean_headers() -> None:
    """한국어 원천 컬럼을 표준 컬럼으로 변환해야 한다."""
    contract = SchemaContract(
        dataset="stores",
        canonical_columns=(
            "year_quarter_code",
            "store_count",
        ),
        aliases={
            "기준_년분기_코드": "year_quarter_code",
            "점포_수": "store_count",
        },
    )

    result = normalize_columns(
        ["기준_년분기_코드", "점포_수"],
        contract,
    )

    assert result == [
        "year_quarter_code",
        "store_count",
    ]


def test_normalize_columns_maps_english_headers() -> None:
    """영문 원천 컬럼도 같은 표준 컬럼으로 변환해야 한다."""
    contract = SchemaContract(
        dataset="stores",
        canonical_columns=(
            "year_quarter_code",
            "store_count",
        ),
        aliases={
            "stdr_yyqu_cd": "year_quarter_code",
            "stor_co": "store_count",
        },
    )

    result = normalize_columns(
        ["stdr_yyqu_cd", "stor_co"],
        contract,
    )

    assert result == [
        "year_quarter_code",
        "store_count",
    ]


def test_normalize_columns_rejects_unexpected_column() -> None:
    """계약에 없는 컬럼이 나타나면 실패해야 한다."""
    contract = make_contract()

    with pytest.raises(
        SchemaContractError,
        match="예상하지 못한 컬럼",
    ):
        normalize_columns(
            [
                *CANONICAL_COLUMNS,
                "unknown_column",
            ],
            contract,
        )


def test_normalize_columns_rejects_alias_collision() -> None:
    """서로 다른 원천 컬럼이 같은 표준 컬럼이 되면 실패해야 한다."""
    contract = SchemaContract(
        dataset="stores",
        canonical_columns=("store_count",),
        aliases={
            "점포_수": "store_count",
            "stor_co": "store_count",
        },
    )

    with pytest.raises(
        SchemaContractError,
        match="중복 표준 컬럼",
    ):
        normalize_columns(
            ["점포_수", "stor_co"],
            contract,
        )


def test_load_schema_contract_reads_toml(
    tmp_path: Path,
) -> None:
    """TOML 파일에서 계약을 읽어야 한다."""
    contract_path = tmp_path / "schema.toml"

    contract_path.write_text(
        """
dataset = "stores"
canonical_columns = ["store_count"]

[aliases]
"점포_수" = "store_count"
""".strip(),
        encoding="utf-8",
    )

    result = load_schema_contract(contract_path)

    assert result.dataset == "stores"
    assert result.canonical_columns == ("store_count",)
    assert result.aliases["점포_수"] == "store_count"