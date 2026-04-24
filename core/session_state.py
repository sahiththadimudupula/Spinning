from __future__ import annotations

import streamlit as st

from calculations.tfo_calculations import (
    apply_tfo_to_master,
    calculate_tfo_manpower_dataframe,
    calculate_tfo_production_dataframe,
)
from config.constants import (
    MASTER_DATA_KEY,
    MASTER_SOURCE_KEY,
    SECTION_ORDER_KEY,
    SUCCESS_MESSAGE_KEY,
    TFO_INPUT_DATA_KEY,
    TFO_MANPOWER_DATA_KEY,
    TFO_PRODUCTION_DATA_KEY,
    TFO_UPLOAD_HASH_KEY,
    WORKBOOK_PATH_KEY,
)
from core.workbook_loader import load_master_dataframe, load_tfo_input_dataframe, resolve_workbook_path


STATEFUL_KEYS = [
    WORKBOOK_PATH_KEY,
    MASTER_SOURCE_KEY,
    MASTER_DATA_KEY,
    TFO_INPUT_DATA_KEY,
    TFO_PRODUCTION_DATA_KEY,
    TFO_MANPOWER_DATA_KEY,
    SECTION_ORDER_KEY,
    SUCCESS_MESSAGE_KEY,
    TFO_UPLOAD_HASH_KEY,
]



def initialize_session_state(force_reload: bool = False) -> None:
    if WORKBOOK_PATH_KEY in st.session_state and not force_reload:
        return

    workbook_path = resolve_workbook_path()
    master_source_df, section_order = load_master_dataframe(workbook_path)
    tfo_input_df = load_tfo_input_dataframe(workbook_path)
    tfo_production_df = calculate_tfo_production_dataframe(tfo_input_df)
    tfo_manpower_df = calculate_tfo_manpower_dataframe(tfo_production_df)
    master_df = apply_tfo_to_master(master_source_df, tfo_manpower_df)

    st.session_state[WORKBOOK_PATH_KEY] = workbook_path
    st.session_state[MASTER_SOURCE_KEY] = master_source_df
    st.session_state[MASTER_DATA_KEY] = master_df
    st.session_state[TFO_INPUT_DATA_KEY] = tfo_input_df
    st.session_state[TFO_PRODUCTION_DATA_KEY] = tfo_production_df
    st.session_state[TFO_MANPOWER_DATA_KEY] = tfo_manpower_df
    st.session_state[SECTION_ORDER_KEY] = section_order
    st.session_state[SUCCESS_MESSAGE_KEY] = ""
    st.session_state[TFO_UPLOAD_HASH_KEY] = ""



def clear_workbook_session_state() -> None:
    for session_key in STATEFUL_KEYS:
        if session_key in st.session_state:
            del st.session_state[session_key]
