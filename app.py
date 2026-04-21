from __future__ import annotations

import streamlit as st

from config.constants import (
    APP_TITLE,
    DEFAULT_OUTPUT_WORKBOOK_PATH,
    MASTER_DATA_KEY,
    SUCCESS_MESSAGE_KEY,
    TFO_INPUT_DATA_KEY,
    TFO_MANPOWER_DATA_KEY,
    TFO_PRODUCTION_DATA_KEY,
    WORKBOOK_PATH_KEY,
    SECTION_ORDER_KEY,
)
from core.session_state import clear_workbook_session_state, initialize_session_state
from core.workbook_writer import build_workbook_bytes, write_state_to_workbook
from ui.components import render_title
from ui.final_master import render_final_master_tab
from ui.main_plan import render_main_plan
from ui.styles import apply_app_styles
from ui.tfo_planning import render_tfo_planning

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_app_styles()
initialize_session_state()

success_message = st.session_state.get(SUCCESS_MESSAGE_KEY, "")
if success_message:
    st.success(success_message)
    st.session_state[SUCCESS_MESSAGE_KEY] = ""

render_title(APP_TITLE)

main_tab, tfo_tab, final_master_tab = st.tabs(
    ["Main Manpower Plan", "TFO Planning", "Final Master Sheet"]
)

with main_tab:
    render_main_plan(
        master_df=st.session_state[MASTER_DATA_KEY],
        section_order=st.session_state[SECTION_ORDER_KEY],
    )

with tfo_tab:
    render_tfo_planning()

with final_master_tab:
    workbook_bytes = build_workbook_bytes(
        workbook_path=st.session_state[WORKBOOK_PATH_KEY],
        master_df=st.session_state[MASTER_DATA_KEY],
        tfo_input_df=st.session_state[TFO_INPUT_DATA_KEY],
        tfo_production_df=st.session_state[TFO_PRODUCTION_DATA_KEY],
        tfo_manpower_df=st.session_state[TFO_MANPOWER_DATA_KEY],
    )
    render_final_master_tab(
        master_df=st.session_state[MASTER_DATA_KEY],
        workbook_bytes=workbook_bytes,
    )

st.markdown('<div class="freeze-wrap"></div>', unsafe_allow_html=True)
action_left, action_center, action_right = st.columns([2.2, 1.6, 2.2])

with action_center:
    if st.button("Freeze Changes", width="stretch"):
        saved_workbook_path = write_state_to_workbook(
            source_workbook_path=st.session_state[WORKBOOK_PATH_KEY],
            output_workbook_path=DEFAULT_OUTPUT_WORKBOOK_PATH,
            master_df=st.session_state[MASTER_DATA_KEY],
            tfo_input_df=st.session_state[TFO_INPUT_DATA_KEY],
            tfo_production_df=st.session_state[TFO_PRODUCTION_DATA_KEY],
            tfo_manpower_df=st.session_state[TFO_MANPOWER_DATA_KEY],
        )
        st.session_state[WORKBOOK_PATH_KEY] = saved_workbook_path
        st.session_state[SUCCESS_MESSAGE_KEY] = "Changes saved to output/Spinning_working.xlsx."
        st.rerun()

reset_left, reset_center, reset_right = st.columns([2.6, 1.2, 2.6])
with reset_center:
    if st.button("Reset from Input", width="stretch"):
        if DEFAULT_OUTPUT_WORKBOOK_PATH.exists():
            DEFAULT_OUTPUT_WORKBOOK_PATH.unlink()
        clear_workbook_session_state()
        initialize_session_state(force_reload=True)
        st.session_state[SUCCESS_MESSAGE_KEY] = "Working file reset. Original input/Spinning.xlsx loaded."
        st.rerun()
