from __future__ import annotations

import pandas as pd

from core.dataframe_utils import clean_text, safe_float


def build_section_summary(master_df: pd.DataFrame, section_order: list[str]) -> pd.DataFrame:
    summary_rows = []

    for section_name in section_order:
        section_df = master_df.loc[master_df["Section"].apply(clean_text) == section_name].copy()
        if section_df.empty:
            continue

        summary_rows.append(
            {
                "Section": section_name,
                "Machine_Count": round(pd.to_numeric(section_df["Machine_Count"], errors="coerce").fillna(0.0).sum(), 2),
                "BE_Final_Manpower": round(pd.to_numeric(section_df["BE_Final_Manpower"], errors="coerce").fillna(0.0).sum(), 2),
            }
        )

    return pd.DataFrame(summary_rows)
