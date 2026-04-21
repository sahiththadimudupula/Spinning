from __future__ import annotations

from io import BytesIO
from pathlib import Path

import openpyxl
import pandas as pd

from config.constants import (
    MASTER_COLUMNS,
    MASTER_SHEET_NAME,
    TFO_INPUT_END_ROW,
    TFO_INPUT_START_ROW,
    TFO_SHEET_NAME,
)
from core.dataframe_utils import clean_text, safe_float


def build_workbook_bytes(
    workbook_path: Path,
    master_df: pd.DataFrame,
    tfo_input_df: pd.DataFrame,
    tfo_production_df: pd.DataFrame,
    tfo_manpower_df: pd.DataFrame,
) -> bytes:
    workbook = openpyxl.load_workbook(workbook_path)
    master_sheet = workbook[MASTER_SHEET_NAME]
    tfo_sheet = workbook[TFO_SHEET_NAME]

    write_master_sheet(master_sheet=master_sheet, master_df=master_df)
    write_tfo_production_section(
        tfo_sheet=tfo_sheet,
        tfo_input_df=tfo_input_df,
        tfo_production_df=tfo_production_df,
    )
    write_tfo_manpower_section(
        tfo_sheet=tfo_sheet,
        tfo_manpower_df=tfo_manpower_df,
    )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()


def write_state_to_workbook(
    source_workbook_path: Path,
    output_workbook_path: Path,
    master_df: pd.DataFrame,
    tfo_input_df: pd.DataFrame,
    tfo_production_df: pd.DataFrame,
    tfo_manpower_df: pd.DataFrame,
) -> Path:
    workbook = openpyxl.load_workbook(source_workbook_path)
    master_sheet = workbook[MASTER_SHEET_NAME]
    tfo_sheet = workbook[TFO_SHEET_NAME]

    write_master_sheet(master_sheet=master_sheet, master_df=master_df)
    write_tfo_production_section(
        tfo_sheet=tfo_sheet,
        tfo_input_df=tfo_input_df,
        tfo_production_df=tfo_production_df,
    )
    write_tfo_manpower_section(
        tfo_sheet=tfo_sheet,
        tfo_manpower_df=tfo_manpower_df,
    )

    output_workbook_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_workbook_path)
    return output_workbook_path


def write_master_sheet(master_sheet, master_df: pd.DataFrame) -> None:
    sorted_df = master_df.sort_values("__excel_row").reset_index(drop=True)

    for _, row in sorted_df.iterrows():
        excel_row = int(row["__excel_row"])

        for column_index, column_name in enumerate(MASTER_COLUMNS, start=1):
            value = row[column_name]
            if pd.isna(value):
                value = None
            master_sheet.cell(row=excel_row, column=column_index, value=value)


def write_tfo_production_section(tfo_sheet, tfo_input_df: pd.DataFrame, tfo_production_df: pd.DataFrame) -> None:
    input_lookup = tfo_input_df.set_index("__excel_row").to_dict("index")
    production_lookup = tfo_production_df.set_index("__excel_row").to_dict("index")

    for excel_row in range(TFO_INPUT_START_ROW, TFO_INPUT_END_ROW + 1):
        input_row = input_lookup.get(excel_row, {})
        production_row = production_lookup.get(excel_row, {})

        tfo_sheet[f"A{excel_row}"] = clean_text(input_row.get("Count"))
        tfo_sheet[f"B{excel_row}"] = clean_text(input_row.get("Customer"))
        tfo_sheet[f"C{excel_row}"] = safe_float(input_row.get("Count2"))
        tfo_sheet[f"D{excel_row}"] = safe_float(input_row.get("Speed"))
        tfo_sheet[f"E{excel_row}"] = safe_float(input_row.get("TPI"))
        tfo_sheet[f"F{excel_row}"] = safe_float(input_row.get("Utilization"))
        tfo_sheet[f"G{excel_row}"] = safe_float(input_row.get("Efficiency"))

        tfo_sheet[f"H{excel_row}"] = production_row.get("Production per Drum/day Formula")
        tfo_sheet[f"I{excel_row}"] = safe_float(production_row.get("Production per Drum/day"))
        tfo_sheet[f"J{excel_row}"] = production_row.get("Production Required / Month Kgs Formula")
        tfo_sheet[f"K{excel_row}"] = safe_float(production_row.get("Production Required / Month Kgs"))
        tfo_sheet[f"L{excel_row}"] = safe_float(input_row.get("Production Required / day Kgs"))
        tfo_sheet[f"M{excel_row}"] = production_row.get("No. of Drums Required Formula")
        tfo_sheet[f"N{excel_row}"] = safe_float(production_row.get("No. of Drums Required"))
        tfo_sheet[f"O{excel_row}"] = production_row.get("TFO Required / Shift Formula")
        tfo_sheet[f"P{excel_row}"] = safe_float(production_row.get("TFO Required / Shift"))
        tfo_sheet[f"Q{excel_row}"] = safe_float(input_row.get("mpm"))
        tfo_sheet[f"R{excel_row}"] = safe_float(input_row.get("Eff"))
        tfo_sheet[f"S{excel_row}"] = production_row.get("kgs/drum/day Formula")
        tfo_sheet[f"T{excel_row}"] = safe_float(production_row.get("kgs/drum/day"))
        tfo_sheet[f"U{excel_row}"] = production_row.get("No. of Drums Formula")
        tfo_sheet[f"V{excel_row}"] = safe_float(production_row.get("No. of Drums (A/W) Reqd."))
        tfo_sheet[f"W{excel_row}"] = production_row.get("Assembly Winding Reqd./ Shift Formula")
        tfo_sheet[f"X{excel_row}"] = safe_float(production_row.get("Assembly Winding Reqd./ Shift"))


def write_tfo_manpower_section(tfo_sheet, tfo_manpower_df: pd.DataFrame) -> None:
    for row_offset, (_, row) in enumerate(tfo_manpower_df.reset_index(drop=True).iterrows()):
        excel_row = 23 + row_offset

        tfo_sheet[f"A{excel_row}"] = clean_text(row["Location"])
        tfo_sheet[f"B{excel_row}"] = clean_text(row["Business"])
        tfo_sheet[f"C{excel_row}"] = clean_text(row["Section"])
        tfo_sheet[f"D{excel_row}"] = safe_float(row["Sr_No"])
        tfo_sheet[f"E{excel_row}"] = clean_text(row["Dept_Machine_Name"])
        tfo_sheet[f"F{excel_row}"] = clean_text(row["Designation"])
        tfo_sheet[f"G{excel_row}"] = None
        tfo_sheet[f"H{excel_row}"] = None
        tfo_sheet[f"I{excel_row}"] = clean_text(row["Formulas"])
        tfo_sheet[f"J{excel_row}"] = safe_float(row["BE_Scientific_Manpower"])
        tfo_sheet[f"K{excel_row}"] = safe_float(row["BE_Final_Manpower"])
        tfo_sheet[f"L{excel_row}"] = safe_float(row["General_Shift"])
        tfo_sheet[f"M{excel_row}"] = safe_float(row["Shift_A"])
        tfo_sheet[f"N{excel_row}"] = safe_float(row["Shift_B"])
        tfo_sheet[f"O{excel_row}"] = safe_float(row["Shift_C"])
        tfo_sheet[f"P{excel_row}"] = safe_float(row["Reliever"])
        tfo_sheet[f"Q{excel_row}"] = clean_text(row["Remarks"])
