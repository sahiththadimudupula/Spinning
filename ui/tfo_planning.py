from __future__ import annotations

import hashlib
from io import BytesIO

import pandas as pd
import streamlit as st

from calculations.tfo_calculations import (
    apply_tfo_to_master,
    calculate_tfo_manpower_dataframe,
    calculate_tfo_production_dataframe,
)
from config.constants import (
    MASTER_DATA_KEY,
    TFO_INPUT_COLUMNS,
    TFO_INPUT_DATA_KEY,
    TFO_MANPOWER_DATA_KEY,
    TFO_PRODUCTION_DATA_KEY,
    TFO_PRODUCTION_DISPLAY_COLUMNS,
    TFO_UPLOAD_HASH_KEY,
    TFO_UPLOAD_OPTIONAL_COLUMNS,
    TFO_UPLOAD_REQUIRED_COLUMNS,
)
from core.dataframe_utils import append_total_row, clean_text, dataframes_match, normalize_key_text, safe_float
from ui.components import render_formula_hover_table, render_metric_cards


UPLOAD_COLUMN_MAP = {
    normalize_key_text("Count"): "Count",
    normalize_key_text("Customer"): "Customer",
    normalize_key_text("Count2"): "Count2",
    normalize_key_text("Speed"): "Speed",
    normalize_key_text("TPI"): "TPI",
    normalize_key_text("Utilization"): "Utilization",
    normalize_key_text("Efficiency"): "Efficiency",
    normalize_key_text("Production Required / day Kgs"): "Production Required / day Kgs",
    normalize_key_text("Production Required / day  Kgs"): "Production Required / day Kgs",
    normalize_key_text("TFO Divisor"): "TFO Divisor",
    normalize_key_text("mpm"): "mpm",
    normalize_key_text("Eff"): "Eff",
    normalize_key_text("Machine Divisor"): "Machine Divisor",
}



def render_tfo_planning() -> None:
    st.markdown('<div class="panel-title">TFO Planning</div>', unsafe_allow_html=True)

    render_tfo_upload()

    current_input_df = st.session_state[TFO_INPUT_DATA_KEY].copy()
    editable_input_df = current_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()
    editable_input_with_total = append_total_row(editable_input_df, label_column="Count")

    st.markdown('<div class="mini-title">TFO Production Planning</div>', unsafe_allow_html=True)
    edited_input_display_df = st.data_editor(
        editable_input_with_total[TFO_INPUT_COLUMNS],
        width="stretch",
        hide_index=True,
        key="tfo_input_editor",
        height=min(56 + max(len(editable_input_with_total), 1) * 35, 560),
        column_config={
            "Count": st.column_config.TextColumn("Count"),
            "Customer": st.column_config.TextColumn("Customer"),
            "Count2": st.column_config.NumberColumn("Count2", format="%.2f"),
            "Speed": st.column_config.NumberColumn("Speed", format="%.2f"),
            "TPI": st.column_config.NumberColumn("TPI", format="%.2f"),
            "Utilization": st.column_config.NumberColumn("Utilization", format="%.2f"),
            "Efficiency": st.column_config.NumberColumn("Efficiency", format="%.2f"),
            "Production Required / day Kgs": st.column_config.NumberColumn("Production Required / day Kgs", format="%.2f"),
            "TFO Divisor": st.column_config.NumberColumn("TFO Divisor", format="%.2f"),
            "mpm": st.column_config.NumberColumn("mpm", format="%.2f"),
            "Eff": st.column_config.NumberColumn("Eff", format="%.2f"),
            "Machine Divisor": st.column_config.NumberColumn("Machine Divisor", format="%.2f"),
        },
    )

    edited_input_df = edited_input_display_df.copy()
    edited_input_df["__excel_row"] = editable_input_with_total["__excel_row"].tolist()
    edited_input_df = edited_input_df.loc[edited_input_df["__excel_row"] != "__TOTAL__"].copy()
    edited_input_df["__excel_row"] = range(2, len(edited_input_df) + 2)
    edited_input_df = normalize_tfo_input_dataframe(edited_input_df)

    current_compare_df = normalize_tfo_input_dataframe(current_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy())
    edited_compare_df = normalize_tfo_input_dataframe(edited_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy())

    if not dataframes_match(current_compare_df, edited_compare_df):
        update_tfo_state(edited_input_df)
        st.rerun()

    production_df = st.session_state[TFO_PRODUCTION_DATA_KEY].copy()
    manpower_df = st.session_state[TFO_MANPOWER_DATA_KEY].copy()

    cards = [
        ("Total TFO Production Reqd.", production_df["Production Required / day Kgs"].sum(), "Current production requirement"),
        ("TFO Reqd./ Shift", production_df["TFO Reqd./ Shift"].sum(), "Calculated from current plan"),
        (
            "Assembly Winding Reqd./ Shift",
            production_df["Assembly Winding Reqd./ Shift"].sum(),
            "Calculated assembly winding requirement",
        ),
        ("No. of Drums (A/W) Reqd.", production_df["No. of Drums (A/W) Reqd."].sum(), "Current drum requirement"),
        ("Total TFO Manpower Reqd./Day", manpower_df["BE_Final_Manpower"].sum(), "Current manpower requirement"),
    ]
    render_metric_cards(cards)

    production_formula_map = {
        "Production Required / Month Kgs": "Production Required / Month Kgs Formula",
        "Production per Drum/day": "Production per Drum/day Formula",
        "No. of Drums Required": "No. of Drums Required Formula",
        "TFO Reqd./ Shift": "TFO Reqd./ Shift Formula",
        "kgs/drum/day": "kgs/drum/day Formula",
        "No. of Drums (A/W) Reqd.": "No. of Drums (A/W) Reqd. Formula",
        "Assembly Winding Reqd./ Shift": "Assembly Winding Reqd./ Shift Formula",
    }

    production_display_df = append_total_row(production_df[TFO_PRODUCTION_DISPLAY_COLUMNS + list(production_formula_map.values())].copy(), label_column="Count")

    st.markdown('<div class="mini-title">TFO Production Result</div>', unsafe_allow_html=True)
    render_formula_hover_table(
        dataframe=production_display_df,
        visible_columns=TFO_PRODUCTION_DISPLAY_COLUMNS,
        formula_columns=production_formula_map,
    )

    manpower_formula_map = {"BE_Scientific_Manpower": "Formulas"}
    manpower_visible_columns = [
        "Dept_Machine_Name",
        "Designation",
        "BE_Scientific_Manpower",
        "BE_Final_Manpower",
        "General_Shift",
        "Shift_A",
        "Shift_B",
        "Shift_C",
        "Reliever",
    ]

    manpower_display_df = append_total_row(manpower_df[manpower_visible_columns + ["Formulas"]].copy(), label_column="Dept_Machine_Name")

    st.markdown('<div class="mini-title">TFO Manpower Requirement</div>', unsafe_allow_html=True)
    render_formula_hover_table(
        dataframe=manpower_display_df,
        visible_columns=manpower_visible_columns,
        formula_columns=manpower_formula_map,
    )



def render_tfo_upload() -> None:
    st.markdown('<div class="mini-title">Upload TFO Input File</div>', unsafe_allow_html=True)
    st.caption(
        "Accepted CSV / Excel columns: Count, Customer, Count2, Speed, TPI, Utilization, Efficiency, "
        "Production Required / day Kgs, mpm, Eff. Optional: TFO Divisor, Machine Divisor."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel for TFO Production Planning",
        type=["csv", "xlsx", "xls"],
        key="tfo_file_uploader",
    )

    if uploaded_file is None:
        return

    file_bytes = uploaded_file.getvalue()
    upload_hash = hashlib.md5(file_bytes).hexdigest()
    if st.session_state.get(TFO_UPLOAD_HASH_KEY) == upload_hash:
        return

    upload_df = read_uploaded_tfo_file(uploaded_file.name, file_bytes)
    normalized_upload_df, missing_columns = normalize_uploaded_tfo_dataframe(upload_df)

    if missing_columns:
        st.error("Missing required columns: " + ", ".join(missing_columns))
        return

    st.session_state[TFO_UPLOAD_HASH_KEY] = upload_hash
    update_tfo_state(normalized_upload_df)
    st.rerun()



def read_uploaded_tfo_file(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    lower_name = file_name.lower()
    if lower_name.endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    return pd.read_excel(BytesIO(file_bytes))



def normalize_uploaded_tfo_dataframe(upload_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    normalized_columns = {}
    for source_column in upload_df.columns:
        mapped_column = UPLOAD_COLUMN_MAP.get(normalize_key_text(source_column))
        if mapped_column:
            normalized_columns[source_column] = mapped_column

    prepared_df = upload_df.rename(columns=normalized_columns).copy()

    missing_columns = [column_name for column_name in TFO_UPLOAD_REQUIRED_COLUMNS if column_name not in prepared_df.columns]
    if missing_columns:
        return pd.DataFrame(), missing_columns

    for optional_column in TFO_UPLOAD_OPTIONAL_COLUMNS:
        if optional_column not in prepared_df.columns:
            prepared_df[optional_column] = 0.0

    prepared_df = prepared_df[TFO_INPUT_COLUMNS].copy()
    prepared_df["__excel_row"] = range(2, len(prepared_df) + 2)
    prepared_df = normalize_tfo_input_dataframe(prepared_df)
    return prepared_df, []



def normalize_tfo_input_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    output_df = dataframe.copy()

    text_columns = ["Count", "Customer"]
    numeric_columns = [column_name for column_name in TFO_INPUT_COLUMNS if column_name not in text_columns]

    for column_name in text_columns:
        output_df[column_name] = output_df[column_name].apply(clean_text)

    for column_name in numeric_columns:
        output_df[column_name] = pd.to_numeric(output_df[column_name], errors="coerce")

    if "TFO Divisor" in output_df.columns:
        output_df["TFO Divisor"] = output_df["TFO Divisor"].astype("float64")
        zero_divisor_mask = output_df["TFO Divisor"].fillna(0.0) <= 0
        replacement_values = output_df.loc[zero_divisor_mask, "Count"].apply(_default_divisor_from_count)
        replacement_values = pd.to_numeric(replacement_values, errors="coerce")
        output_df.loc[zero_divisor_mask, "TFO Divisor"] = replacement_values.to_numpy(dtype="float64")
        output_df["TFO Divisor"] = output_df["TFO Divisor"].fillna(0.0).round(2)

    if "Machine Divisor" in output_df.columns:
        output_df["Machine Divisor"] = output_df["Machine Divisor"].astype("float64")
        zero_machine_mask = output_df["Machine Divisor"].fillna(0.0) <= 0
        output_df.loc[zero_machine_mask, "Machine Divisor"] = 72.0
        output_df["Machine Divisor"] = output_df["Machine Divisor"].fillna(0.0).round(2)

    for column_name in numeric_columns:
        output_df[column_name] = pd.to_numeric(output_df[column_name], errors="coerce").fillna(0.0).round(2)

    if "__excel_row" not in output_df.columns:
        output_df["__excel_row"] = range(2, len(output_df) + 2)

    output_df["__excel_row"] = range(2, len(output_df) + 2)
    return output_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()



def _default_divisor_from_count(count_value: object) -> float:
    return 80.0 if normalize_key_text(count_value) == normalize_key_text("4/2/6 K") else 240.0



def update_tfo_state(tfo_input_df: pd.DataFrame) -> None:
    refreshed_production_df = calculate_tfo_production_dataframe(tfo_input_df)
    refreshed_manpower_df = calculate_tfo_manpower_dataframe(refreshed_production_df)
    refreshed_master_df = apply_tfo_to_master(st.session_state[MASTER_DATA_KEY], refreshed_manpower_df)

    st.session_state[TFO_INPUT_DATA_KEY] = tfo_input_df
    st.session_state[TFO_PRODUCTION_DATA_KEY] = refreshed_production_df
    st.session_state[TFO_MANPOWER_DATA_KEY] = refreshed_manpower_df
    st.session_state[MASTER_DATA_KEY] = refreshed_master_df
