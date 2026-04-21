from __future__ import annotations

import pandas as pd
import streamlit as st

from calculations.summary_calculations import build_section_summary
from config.constants import EDITOR_COLUMNS, OPERATOR_TYPE_OPTIONS
from core.dataframe_utils import (
    append_total_row,
    coerce_editor_dataframe,
    dataframes_match,
    normalize_key_text,
    safe_float,
    unique_strings_in_order,
)
from ui.components import render_metric_cards


COMPACT_COLUMNS = ["Section", "Dept_Machine_Name", "Designation", "BE_Final_Manpower"]
EDITABLE_COLUMNS_TO_SAVE = [
    "Operator_Type",
    "Contractors",
    "Company_Associate",
    "BE_Final_Manpower",
    "General_Shift",
    "Shift_A",
    "Shift_B",
    "Shift_C",
    "Reliever",
    "Remarks",
]


def render_main_plan(master_df: pd.DataFrame, section_order: list[str]) -> None:
    st.markdown('<div class="panel-title">Main Manpower Plan</div>', unsafe_allow_html=True)

    selected_sections, selected_designations = render_filters(master_df)
    filtered_df = apply_filters(
        master_df=master_df,
        selected_sections=selected_sections,
        selected_designations=selected_designations,
        section_order=section_order,
    )

    visible_sections = [section_name for section_name in section_order if section_name in filtered_df["Section"].tolist()]

    cards = [
        ("Section", len(visible_sections), "Number of visible sections"),
        (
            "Sum of BE_Final_Manpower",
            round(pd.to_numeric(filtered_df["BE_Final_Manpower"], errors="coerce").fillna(0.0).sum(), 2),
            "Current filtered manpower total",
        ),
    ]
    render_metric_cards(cards)

    summary_df = build_section_summary(filtered_df, visible_sections)
    summary_display_df = append_total_row(summary_df, label_column="Section")

    st.markdown('<div class="mini-title">Section Summary</div>', unsafe_allow_html=True)
    st.dataframe(
        summary_display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Machine_Count": st.column_config.NumberColumn("Machine_Count", format="%.2f"),
            "BE_Final_Manpower": st.column_config.NumberColumn("BE_Final_Manpower", format="%.2f"),
        },
    )

    for section_name in visible_sections:
        section_df = filtered_df.loc[filtered_df["Section"] == section_name].copy()
        if section_df.empty:
            continue

        render_section_block(section_name=section_name, section_df=section_df)


def render_filters(master_df: pd.DataFrame) -> tuple[list[str], list[str]]:
    st.markdown('<div class="mini-title">Filters</div>', unsafe_allow_html=True)

    section_options = unique_strings_in_order(master_df["Section"].tolist())
    designation_options = unique_strings_in_order(master_df["Designation"].tolist())

    filter_col_1, filter_col_2 = st.columns(2)

    with filter_col_1:
        selected_sections = st.multiselect(
            "Section",
            options=section_options,
            default=[],
        )

    with filter_col_2:
        selected_designations = st.multiselect(
            "Designation",
            options=designation_options,
            default=[],
        )

    return selected_sections, selected_designations


def apply_filters(
    master_df: pd.DataFrame,
    selected_sections: list[str],
    selected_designations: list[str],
    section_order: list[str],
) -> pd.DataFrame:
    filtered_df = master_df.copy()

    if selected_sections:
        filtered_df = filtered_df.loc[filtered_df["Section"].isin(selected_sections)].copy()

    if selected_designations:
        filtered_df = filtered_df.loc[filtered_df["Designation"].isin(selected_designations)].copy()

    section_rank = {section_name: index for index, section_name in enumerate(section_order)}
    filtered_df["__section_rank"] = filtered_df["Section"].map(section_rank).fillna(9999)
    filtered_df = filtered_df.sort_values(["__section_rank", "__excel_row"]).drop(columns=["__section_rank"])

    return filtered_df


def render_section_block(section_name: str, section_df: pd.DataFrame) -> None:
    st.markdown(f'<div class="section-shell"><div class="section-name">{section_name}</div>', unsafe_allow_html=True)

    compact_df = append_total_row(section_df[COMPACT_COLUMNS].copy(), label_column="Section")
    st.dataframe(
        compact_df,
        width="stretch",
        hide_index=True,
        column_config={
            "BE_Final_Manpower": st.column_config.NumberColumn("BE_Final_Manpower", format="%.2f"),
        },
    )

    is_tfo_section = normalize_key_text(section_name) == "TFO"

    with st.expander(f"Expand {section_name}", expanded=False):
        editable_df = section_df[EDITOR_COLUMNS + ["__row_key"]].copy()
        editable_df_with_total = append_total_row(editable_df, label_column="Section", total_row_key="__TOTAL__")
        editable_display_df = editable_df_with_total[EDITOR_COLUMNS].copy()

        if is_tfo_section:
            st.info("TFO rows are controlled from TFO Planning.")
            st.dataframe(
                editable_display_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Contractors": st.column_config.NumberColumn("Contractors", format="%.2f"),
                    "Company_Associate": st.column_config.NumberColumn("Company_Associate", format="%.2f"),
                    "BE_Final_Manpower": st.column_config.NumberColumn("BE_Final_Manpower", format="%.2f"),
                    "General_Shift": st.column_config.NumberColumn("General_Shift", format="%.2f"),
                    "Shift_A": st.column_config.NumberColumn("Shift_A", format="%.2f"),
                    "Shift_B": st.column_config.NumberColumn("Shift_B", format="%.2f"),
                    "Shift_C": st.column_config.NumberColumn("Shift_C", format="%.2f"),
                    "Reliever": st.column_config.NumberColumn("Reliever", format="%.2f"),
                },
            )
        else:
            edited_display_df = st.data_editor(
                editable_display_df,
                width="stretch",
                hide_index=True,
                key=f"editor_{section_name}",
                column_config={
                    "Operator_Type": st.column_config.SelectboxColumn("Operator_Type", options=OPERATOR_TYPE_OPTIONS),
                    "Contractors": st.column_config.NumberColumn("Contractors", format="%.2f"),
                    "Company_Associate": st.column_config.NumberColumn("Company_Associate", format="%.2f"),
                    "BE_Final_Manpower": st.column_config.NumberColumn("BE_Final_Manpower", format="%.2f"),
                    "General_Shift": st.column_config.NumberColumn("General_Shift", format="%.2f"),
                    "Shift_A": st.column_config.NumberColumn("Shift_A", format="%.2f"),
                    "Shift_B": st.column_config.NumberColumn("Shift_B", format="%.2f"),
                    "Shift_C": st.column_config.NumberColumn("Shift_C", format="%.2f"),
                    "Reliever": st.column_config.NumberColumn("Reliever", format="%.2f"),
                    "Section": st.column_config.TextColumn("Section", disabled=True),
                    "Dept_Machine_Name": st.column_config.TextColumn("Dept_Machine_Name", disabled=True),
                    "Designation": st.column_config.TextColumn("Designation", disabled=True),
                },
            )
            persist_section_edits(
                original_df=editable_df,
                editable_df_with_total=editable_df_with_total,
                edited_display_df=edited_display_df,
            )

    st.markdown("</div>", unsafe_allow_html=True)


def persist_section_edits(
    original_df: pd.DataFrame,
    editable_df_with_total: pd.DataFrame,
    edited_display_df: pd.DataFrame,
) -> None:
    from config.constants import MASTER_DATA_KEY

    edited_df = edited_display_df.copy()
    edited_df["__row_key"] = editable_df_with_total["__row_key"].tolist()
    edited_df = edited_df.loc[edited_df["__row_key"] != "__TOTAL__"].copy()
    edited_df = coerce_editor_dataframe(edited_df)

    compare_original = original_df[EDITOR_COLUMNS + ["__row_key"]].copy()
    compare_original = coerce_editor_dataframe(compare_original)

    if dataframes_match(compare_original, edited_df[EDITOR_COLUMNS + ["__row_key"]]):
        return

    current_master_df = st.session_state[MASTER_DATA_KEY].copy()
    update_lookup = edited_df.set_index("__row_key")[EDITABLE_COLUMNS_TO_SAVE].to_dict("index")

    for row_index, row in current_master_df.iterrows():
        row_key = row["__row_key"]
        if row_key not in update_lookup:
            continue

        for column_name in EDITABLE_COLUMNS_TO_SAVE:
            current_master_df.at[row_index, column_name] = update_lookup[row_key][column_name]

    st.session_state[MASTER_DATA_KEY] = current_master_df
    st.rerun()
