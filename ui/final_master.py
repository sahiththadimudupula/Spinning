from __future__ import annotations

import pandas as pd
import streamlit as st

from config.constants import MASTER_COLUMNS



def render_final_master_tab(master_df: pd.DataFrame, workbook_bytes: bytes) -> None:
    st.markdown('<div class="panel-title">Final Master Sheet</div>', unsafe_allow_html=True)

    display_df = master_df[MASTER_COLUMNS].copy()

    st.download_button(
        label="Download Full Excel",
        data=workbook_bytes,
        file_name="Vapi_Spinning_Manpower_Engine_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Machine_Count": st.column_config.NumberColumn("Machine_Count", format="%.2f"),
            "BE_Scientific_Manpower": st.column_config.NumberColumn("BE_Scientific_Manpower", format="%.2f"),
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
