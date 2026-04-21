from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import (
    MASTER_DATA_KEY,
    TFO_INPUT_COLUMNS,
    TFO_INPUT_DATA_KEY,
    TFO_MANPOWER_DATA_KEY,
    TFO_PRODUCTION_DATA_KEY,
    TFO_PRODUCTION_DISPLAY_COLUMNS,
)
from core.dataframe_utils import append_total_row, dataframes_match
from ui.components import render_formula_hover_table, render_metric_cards



def render_tfo_planning() -> None:
    from calculations.tfo_calculations import (
        apply_tfo_to_master,
        calculate_tfo_manpower_dataframe,
        calculate_tfo_production_dataframe,
    )

    st.markdown('<div class="panel-title">TFO Planning</div>', unsafe_allow_html=True)

    current_input_df = st.session_state[TFO_INPUT_DATA_KEY].copy()
    editable_input_df = current_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()
    editable_input_with_total = append_total_row(editable_input_df, label_column="Count")

    st.markdown('<div class="mini-title">TFO Production Planning</div>', unsafe_allow_html=True)
    edited_input_display_df = st.data_editor(
        editable_input_with_total[TFO_INPUT_COLUMNS],
        width="stretch",
        hide_index=True,
        key="tfo_input_editor",
        column_config={
            "Count": st.column_config.TextColumn("Count"),
            "Customer": st.column_config.TextColumn("Customer"),
            "Count2": st.column_config.NumberColumn("Count2", format="%.2f"),
            "Speed": st.column_config.NumberColumn("Speed", format="%.2f"),
            "TPI": st.column_config.NumberColumn("TPI", format="%.2f"),
            "Utilization": st.column_config.NumberColumn("Utilization", format="%.2f"),
            "Efficiency": st.column_config.NumberColumn("Efficiency", format="%.2f"),
            "Production Required / day Kgs": st.column_config.NumberColumn("Production Required / day Kgs", format="%.2f"),
            "mpm": st.column_config.NumberColumn("mpm", format="%.2f"),
            "Eff": st.column_config.NumberColumn("Eff", format="%.2f"),
        },
    )

    edited_input_df = edited_input_display_df.copy()
    edited_input_df["__excel_row"] = editable_input_with_total["__excel_row"].tolist()
    edited_input_df = edited_input_df.loc[edited_input_df["__excel_row"] != "__TOTAL__"].copy()

    current_compare_df = current_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()
    edited_compare_df = edited_input_df[TFO_INPUT_COLUMNS + ["__excel_row"]].copy()

    if not dataframes_match(current_compare_df, edited_compare_df):
        st.session_state[TFO_INPUT_DATA_KEY] = edited_input_df
        refreshed_production_df = calculate_tfo_production_dataframe(edited_input_df)
        refreshed_manpower_df = calculate_tfo_manpower_dataframe(refreshed_production_df)
        refreshed_master_df = apply_tfo_to_master(st.session_state[MASTER_DATA_KEY], refreshed_manpower_df)

        st.session_state[TFO_PRODUCTION_DATA_KEY] = refreshed_production_df
        st.session_state[TFO_MANPOWER_DATA_KEY] = refreshed_manpower_df
        st.session_state[MASTER_DATA_KEY] = refreshed_master_df
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

    production_display_df = append_total_row(
        production_df[TFO_PRODUCTION_DISPLAY_COLUMNS].copy(),
        label_column="Count",
    )

    st.markdown('<div class="mini-title">TFO Production Result</div>', unsafe_allow_html=True)
    render_formula_hover_table(
        dataframe=production_display_df,
        visible_columns=TFO_PRODUCTION_DISPLAY_COLUMNS,
        formula_columns=production_formula_map,
    )

    manpower_formula_map = {
        "BE_Scientific_Manpower": "Formulas",
    }
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

    manpower_display_df = append_total_row(
        manpower_df[manpower_visible_columns + ["Formulas"]].copy(),
        label_column="Dept_Machine_Name",
    )

    st.markdown('<div class="mini-title">TFO Manpower Requirement</div>', unsafe_allow_html=True)
    render_formula_hover_table(
        dataframe=manpower_display_df,
        visible_columns=manpower_visible_columns,
        formula_columns=manpower_formula_map,
    )
