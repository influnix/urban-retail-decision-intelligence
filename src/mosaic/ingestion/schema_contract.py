"""원천 데이터 컬럼을 MOSAIC 표준 스키마로 변환한다."""

from __future__ import annotations

import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class SchemaContract:
    """하나의 데이터셋에 적용할 컬럼 계약."""

    dataset: str
    canonical_columns: tuple[str, ...]
    aliases: dict[str, str]


class SchemaContractError(ValueError):
    """원천 스키마가 계약을 만족하지 않을 때 발생한다."""


def load_schema_contract(path: Path) -> SchemaContract:
    """TOML 파일에서 스키마 계약을 읽는다."""
    with path.open("rb") as file:
        data = tomllib.load(file)

    dataset = data.get("dataset")
    canonical_columns = data.get("canonical_columns")
    aliases = data.get("aliases")

    if not isinstance(dataset, str) or not dataset:
        raise SchemaContractError(
            "dataset은 비어 있지 않은 문자열이어야 한다."
        )

    if not isinstance(canonical_columns, list) or not all(
        isinstance(column, str)
        for column in canonical_columns
    ):
        raise SchemaContractError(
            "canonical_columns는 문자열 목록이어야 한다."
        )

    if len(canonical_columns) != len(set(canonical_columns)):
        raise SchemaContractError(
            "canonical_columns에 중복 컬럼이 있다."
        )

    if not isinstance(aliases, dict) or not all(
        isinstance(source, str)
        and isinstance(target, str)
        for source, target in aliases.items()
    ):
        raise SchemaContractError(
            "aliases는 문자열 간 매핑이어야 한다."
        )

    invalid_targets = sorted(
        {
            target
            for target in aliases.values()
            if target not in canonical_columns
        }
    )

    if invalid_targets:
        raise SchemaContractError(
            "aliases의 대상이 표준 컬럼에 없다: "
            f"{invalid_targets}"
        )

    return SchemaContract(
        dataset=dataset,
        canonical_columns=tuple(canonical_columns),
        aliases=dict(aliases),
    )


def normalize_columns(
    source_columns: Sequence[str],
    contract: SchemaContract,
) -> list[str]:
    """원천 컬럼을 표준 컬럼으로 변환하고 계약을 검증한다."""
    normalized_columns = [
        contract.aliases.get(column, column)
        for column in source_columns
    ]

    counts = Counter(normalized_columns)

    duplicate_columns = sorted(
        column
        for column, count in counts.items()
        if count > 1
    )

    missing_columns = sorted(
        set(contract.canonical_columns)
        - set(normalized_columns)
    )

    unexpected_columns = sorted(
        set(normalized_columns)
        - set(contract.canonical_columns)
    )

    errors: list[str] = []

    if duplicate_columns:
        errors.append(
            f"중복 표준 컬럼: {duplicate_columns}"
        )

    if missing_columns:
        errors.append(
            f"누락된 필수 컬럼: {missing_columns}"
        )

    if unexpected_columns:
        errors.append(
            f"예상하지 못한 컬럼: {unexpected_columns}"
        )

    if errors:
        raise SchemaContractError("; ".join(errors))

    return list(contract.canonical_columns)