from __future__ import annotations

import math
from typing import Iterable

import pandas as pd

from config.constants import EDITABLE_NUMERIC_COLUMNS, NUMERIC_COLUMNS, TEXT_COLUMNS


def clean_text(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def normalize_key_text(value: object) -> str:
    return " ".join(clean_text(value).upper().split())


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def format_number(value: object, digits: int = 2) -> str:
    number = safe_float(value, 0.0)
    return f"{number:,.{digits}f}"


def coerce_master_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    output_df = dataframe.copy()

    for column_name in NUMERIC_COLUMNS:
        if column_name in output_df.columns:
            output_df[column_name] = pd.to_numeric(output_df[column_name], errors="coerce")

    for column_name in TEXT_COLUMNS:
        if column_name in output_df.columns:
            output_df[column_name] = output_df[column_name].apply(clean_text)

    return output_df


def coerce_editor_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    output_df = dataframe.copy()

    for column_name in EDITABLE_NUMERIC_COLUMNS:
        if column_name in output_df.columns:
            output_df[column_name] = pd.to_numeric(output_df[column_name], errors="coerce").fillna(0.0)

    for column_name in output_df.columns:
        if column_name not in EDITABLE_NUMERIC_COLUMNS:
            output_df[column_name] = output_df[column_name].apply(clean_text)

    return output_df


def unique_strings_in_order(values: Iterable[object]) -> list[str]:
    ordered_values: list[str] = []
    seen_values: set[str] = set()

    for value in values:
        text_value = clean_text(value)
        if not text_value:
            continue

        normalized = normalize_key_text(text_value)
        if normalized in seen_values:
            continue

        seen_values.add(normalized)
        ordered_values.append(text_value)

    return ordered_values


def normalize_compare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    compare_df = dataframe.copy()

    for column_name in compare_df.columns:
        if column_name in EDITABLE_NUMERIC_COLUMNS or column_name in NUMERIC_COLUMNS:
            compare_df[column_name] = pd.to_numeric(compare_df[column_name], errors="coerce").fillna(0.0).round(4)
        else:
            compare_df[column_name] = compare_df[column_name].apply(clean_text)

    return compare_df.reset_index(drop=True)


def dataframes_match(left_df: pd.DataFrame, right_df: pd.DataFrame) -> bool:
    return normalize_compare_dataframe(left_df).equals(normalize_compare_dataframe(right_df))


def split_shift_evenly(total_manpower: float) -> tuple[float, float, float, float]:
    total_value = int(round(safe_float(total_manpower)))
    shift_a = total_value // 3
    shift_b = total_value // 3
    shift_c = total_value // 3
    remainder = total_value - (shift_a + shift_b + shift_c)

    if remainder >= 1:
        shift_a += 1
    if remainder >= 2:
        shift_b += 1

    return 0.0, float(shift_a), float(shift_b), float(shift_c)
