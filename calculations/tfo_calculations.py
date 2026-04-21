from __future__ import annotations

import math

import pandas as pd

from config.constants import (
    DEFAULT_MACHINE_DIVISOR,
    DEFAULT_TFO_DIVISOR,
    MASTER_COLUMNS,
    SPECIAL_TFO_COUNT,
    SPECIAL_TFO_DIVISOR,
)
from core.dataframe_utils import clean_text, normalize_key_text, safe_float, split_shift_evenly


def excel_round(value: float, digits: int = 0) -> float:
    return round(value, digits)


def excel_roundup(value: float, digits: int = 0) -> float:
    factor = 10 ** digits
    return math.ceil(value * factor) / factor


def get_tfo_divisor(count_value: object) -> float:
    normalized_count = normalize_key_text(count_value)
    if normalized_count == normalize_key_text(SPECIAL_TFO_COUNT):
        return SPECIAL_TFO_DIVISOR
    return DEFAULT_TFO_DIVISOR


def build_formula_texts(excel_row: int, divisor: float) -> dict[str, str]:
    divisor_text = int(divisor) if divisor == int(divisor) else divisor

    return {
        "Production per Drum/day Formula": f"=((D{excel_row}*60*8*G{excel_row}*2)/(E{excel_row}*36*840*C{excel_row}*2.202))*3",
        "Production Required / Month Kgs Formula": f"=L{excel_row}*30",
        "No. of Drums Required Formula": f"=L{excel_row}/I{excel_row}",
        "TFO Reqd./ Shift Formula": f"=N{excel_row}/{divisor_text}",
        "kgs/drum/day Formula": f"=(Q{excel_row}*R{excel_row}*8*60*1.09/(C{excel_row}*840*2.202))*3",
        "No. of Drums (A/W) Reqd. Formula": f"=L{excel_row}/T{excel_row}",
        "Assembly Winding Reqd./ Shift Formula": f"=V{excel_row}/{int(DEFAULT_MACHINE_DIVISOR)}",
        "TFO Required / Shift Formula": f"=N{excel_row}/{divisor_text}",
        "No. of Drums Formula": f"=L{excel_row}/T{excel_row}",
        "No. of Machines Formula": f"=V{excel_row}/{int(DEFAULT_MACHINE_DIVISOR)}",
    }


def calculate_tfo_production_dataframe(tfo_input_df: pd.DataFrame) -> pd.DataFrame:
    output_rows = []

    for row_number, row in tfo_input_df.reset_index(drop=True).iterrows():
        excel_row = int(row.get("__excel_row", row_number + 2))
        divisor = get_tfo_divisor(row.get("Count"))

        count2 = safe_float(row.get("Count2"))
        speed = safe_float(row.get("Speed"))
        tpi = safe_float(row.get("TPI"))
        efficiency = safe_float(row.get("Efficiency"))
        production_required_day = safe_float(row.get("Production Required / day Kgs"))
        mpm = safe_float(row.get("mpm"))
        eff_value = safe_float(row.get("Eff"))

        if count2 > 0 and tpi > 0 and speed > 0 and efficiency > 0:
            production_per_drum_day = ((speed * 60 * 8 * efficiency * 2) / (tpi * 36 * 840 * count2 * 2.202)) * 3
        else:
            production_per_drum_day = 0.0

        production_required_month = production_required_day * 30
        drums_required = production_required_day / production_per_drum_day if production_per_drum_day > 0 else 0.0
        tfo_required_shift = drums_required / divisor if divisor > 0 else 0.0

        if count2 > 0 and mpm > 0 and eff_value > 0:
            kilograms_per_drum_day = ((mpm * eff_value * 8 * 60 * 1.09) / (count2 * 840 * 2.202)) * 3
        else:
            kilograms_per_drum_day = 0.0

        no_of_drums = production_required_day / kilograms_per_drum_day if kilograms_per_drum_day > 0 else 0.0
        assembly_winding_required_shift = no_of_drums / DEFAULT_MACHINE_DIVISOR if DEFAULT_MACHINE_DIVISOR > 0 else 0.0

        output_row = {
            "Count": clean_text(row.get("Count")),
            "Customer": clean_text(row.get("Customer")),
            "Count2": round(count2, 2),
            "Speed": round(speed, 2),
            "TPI": round(tpi, 2),
            "Utilization": round(safe_float(row.get("Utilization")), 2),
            "Efficiency": round(efficiency, 2),
            "Production Required / day Kgs": round(production_required_day, 2),
            "Production Required / Month Kgs": round(production_required_month, 2),
            "Production per Drum/day": round(production_per_drum_day, 2),
            "No. of Drums Required": round(drums_required, 2),
            "TFO Reqd./ Shift": round(tfo_required_shift, 2),
            "TFO Required / Shift": round(tfo_required_shift, 2),
            "mpm": round(mpm, 2),
            "Eff": round(eff_value, 2),
            "kgs/drum/day": round(kilograms_per_drum_day, 2),
            "No. of Drums (A/W) Reqd.": round(no_of_drums, 2),
            "No. of Drums": round(no_of_drums, 2),
            "Assembly Winding Reqd./ Shift": round(assembly_winding_required_shift, 2),
            "No. of Machines": round(assembly_winding_required_shift, 2),
            "TFO Divisor": divisor,
            "Machine Divisor": DEFAULT_MACHINE_DIVISOR,
            "__excel_row": excel_row,
        }
        output_row.update(build_formula_texts(excel_row=excel_row, divisor=divisor))
        output_rows.append(output_row)

    return pd.DataFrame(output_rows)


def calculate_tfo_manpower_dataframe(production_df: pd.DataFrame) -> pd.DataFrame:
    non_special_df = production_df.loc[
        production_df["Count"].apply(normalize_key_text) != normalize_key_text(SPECIAL_TFO_COUNT)
    ].copy()

    special_df = production_df.loc[
        production_df["Count"].apply(normalize_key_text) == normalize_key_text(SPECIAL_TFO_COUNT)
    ].copy()

    special_drums = safe_float(special_df["No. of Drums (A/W) Reqd."].sum())
    total_drums_non_special = safe_float(non_special_df["No. of Drums (A/W) Reqd."].sum())
    total_tfo_required_non_special = safe_float(non_special_df["TFO Reqd./ Shift"].sum())

    assembly_winding = excel_roundup((((total_drums_non_special / 36) + (special_drums / 36)) * 3), 0)
    jumbo_assembly_winding = excel_round(excel_roundup(special_drums, 0) / 16, 0) * 2
    tfo_operator = excel_round(total_tfo_required_non_special / 6, 0) * 3
    tfo_operator_doffer = excel_roundup(total_tfo_required_non_special / 4, 0) * 3

    base_rows = [
        (1, "Assembly winding", "operator", "ROUNDUP((((SUM(T2:T18)/36)+(T19/36))*3),0)", assembly_winding),
        (2, "Jumbo Assembly Winding", "operator", "ROUND(ROUNDUP(T19,0)/16,0)*2", jumbo_assembly_winding),
        (3, "TFO", "TFO Operator", "ROUND(+SUM(N2:N18)/6,0)*3", tfo_operator),
        (4, "TFO", "TFO Operator (Doffer)", "ROUNDUP(+SUM(N2:N18)/4,0)*3", tfo_operator_doffer),
        (5, "Jumbo TFO", "TFO Operator", "2*3", 6.0),
        (6, "Vijaylakshmi TFO", "TFO Operator", "2*3", 6.0),
        (7, "Jobber", "Jobber", "1*3", 3.0),
        (8, "Cone Carrier", "Cone carrier", "1*3", 3.0),
        (9, "Cone Checker", "Cone checker", "2*3", 6.0),
        (10, "Cone tipping", "", "1*3", 3.0),
        (11, "Fork lift opt", "", "1*1", 1.0),
        (12, "Packer", "", "4*3", 12.0),
        (13, "Packing Jobber", "Jobber", "0*3", 0.0),
        (15, "DEO", "DEO", "1*1", 1.0),
        (16, "House Keeper", "Contractors", "2*3", 6.0),
    ]

    manpower_rows = []

    for sr_no, machine_name, designation, formula_text, scientific_value in base_rows:
        general_shift, shift_a, shift_b, shift_c = split_shift_evenly(scientific_value)
        manpower_rows.append(
            {
                "Location": "Vapi",
                "Business": "Spinning",
                "Section": "TFO",
                "Sr_No": sr_no,
                "Dept_Machine_Name": machine_name,
                "Designation": designation,
                "Machine_Count": 0.0,
                "Workload": "",
                "Formulas": formula_text,
                "BE_Scientific_Manpower": round(scientific_value, 2),
                "Operator_Type": "",
                "Contractors": 0.0,
                "Company_Associate": 0.0,
                "BE_Final_Manpower": round(scientific_value, 2),
                "General_Shift": round(general_shift, 2),
                "Shift_A": round(shift_a, 2),
                "Shift_B": round(shift_b, 2),
                "Shift_C": round(shift_c, 2),
                "Reliever": 0.0,
                "Remarks": "",
            }
        )

    return pd.DataFrame(manpower_rows)[MASTER_COLUMNS].copy()


def apply_tfo_to_master(master_df: pd.DataFrame, tfo_manpower_df: pd.DataFrame) -> pd.DataFrame:
    updated_df = master_df.copy()
    updated_df["__sr_no_key"] = pd.to_numeric(updated_df["Sr_No"], errors="coerce").fillna(-1).astype(int)

    tfo_rows = updated_df["Section"].apply(normalize_key_text) == "TFO"
    tfo_lookup = tfo_manpower_df.copy()
    tfo_lookup["__sr_no_key"] = pd.to_numeric(tfo_lookup["Sr_No"], errors="coerce").fillna(-1).astype(int)

    update_columns = [
        "Formulas",
        "BE_Scientific_Manpower",
        "BE_Final_Manpower",
        "General_Shift",
        "Shift_A",
        "Shift_B",
        "Shift_C",
        "Reliever",
        "Remarks",
        "Designation",
        "Dept_Machine_Name",
    ]

    for _, tfo_row in tfo_lookup.iterrows():
        row_mask = tfo_rows & (updated_df["__sr_no_key"] == int(tfo_row["__sr_no_key"]))
        if not row_mask.any():
            continue

        row_index = updated_df.index[row_mask][0]
        for column_name in update_columns:
            updated_df.at[row_index, column_name] = tfo_row[column_name]

    return updated_df.drop(columns=["__sr_no_key"], errors="ignore")
