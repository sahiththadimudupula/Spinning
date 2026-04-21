from __future__ import annotations

from pathlib import Path

import openpyxl
import pandas as pd

from config.constants import (
    INPUT_WORKBOOK_CANDIDATES,
    MASTER_COLUMNS,
    MASTER_SHEET_NAME,
    OUTPUT_WORKBOOK_CANDIDATES,
    TFO_INPUT_COLUMNS,
    TFO_INPUT_END_ROW,
    TFO_INPUT_START_ROW,
    TFO_SHEET_NAME,
)
from core.dataframe_utils import clean_text, coerce_master_dataframe, safe_float


def get_input_workbook_path() -> Path:
    for candidate_path in INPUT_WORKBOOK_CANDIDATES:
        if candidate_path.exists():
            return candidate_path
    raise FileNotFoundError("input/Spinning.xlsx not found.")


def get_output_workbook_path() -> Path:
    for candidate_path in OUTPUT_WORKBOOK_CANDIDATES:
        if candidate_path.exists():
            return candidate_path
    return OUTPUT_WORKBOOK_CANDIDATES[0]


def resolve_workbook_path() -> Path:
    output_workbook_path = get_output_workbook_path()
    if output_workbook_path.exists():
        return output_workbook_path
    return get_input_workbook_path()


def load_master_dataframe(workbook_path: Path) -> tuple[pd.DataFrame, list[str]]:
    master_df = pd.read_excel(workbook_path, sheet_name=MASTER_SHEET_NAME)

    for column_name in MASTER_COLUMNS:
        if column_name not in master_df.columns:
            master_df[column_name] = ""

    master_df = master_df[MASTER_COLUMNS].copy()
    master_df["__excel_row"] = range(2, len(master_df) + 2)
    master_df["__row_key"] = master_df["__excel_row"].apply(lambda row_number: f"ROW_{row_number}")

    section_order = []
    seen_sections = set()

    for section_name in master_df["Section"].tolist():
        section_text = clean_text(section_name)
        if not section_text:
            continue
        normalized_section = section_text.upper()
        if normalized_section in seen_sections:
            continue
        seen_sections.add(normalized_section)
        section_order.append(section_text)

    return coerce_master_dataframe(master_df), section_order


def load_tfo_input_dataframe(workbook_path: Path) -> pd.DataFrame:
    workbook = openpyxl.load_workbook(workbook_path, data_only=False)
    sheet = workbook[TFO_SHEET_NAME]

    rows = []
    for excel_row in range(TFO_INPUT_START_ROW, TFO_INPUT_END_ROW + 1):
        count_value = sheet[f"A{excel_row}"].value
        customer_value = sheet[f"B{excel_row}"].value

        rows.append(
            {
                "Count": clean_text(count_value),
                "Customer": clean_text(customer_value),
                "Count2": safe_float(sheet[f"C{excel_row}"].value),
                "Speed": safe_float(sheet[f"D{excel_row}"].value),
                "TPI": safe_float(sheet[f"E{excel_row}"].value),
                "Utilization": safe_float(sheet[f"F{excel_row}"].value),
                "Efficiency": safe_float(sheet[f"G{excel_row}"].value),
                "Production Required / day Kgs": safe_float(sheet[f"L{excel_row}"].value),
                "mpm": safe_float(sheet[f"Q{excel_row}"].value),
                "Eff": safe_float(sheet[f"R{excel_row}"].value),
                "__excel_row": excel_row,
            }
        )

    tfo_input_df = pd.DataFrame(rows)
    return tfo_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()
