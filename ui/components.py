from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from core.dataframe_utils import format_number



def render_title(title_text: str) -> None:
    st.markdown(f'<div class="app-title">{html.escape(title_text)}</div>', unsafe_allow_html=True)



def render_metric_cards(cards: list[tuple[str, object, str]]) -> None:
    if not cards:
        return

    columns = st.columns(len(cards))
    for column, (label_text, value, note_text) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{html.escape(str(label_text))}</div>
                    <div class="metric-value">{html.escape(format_number(value))}</div>
                    <div class="metric-note">{html.escape(str(note_text))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )



def render_formula_hover_table(
    dataframe: pd.DataFrame,
    visible_columns: list[str],
    formula_columns: dict[str, str] | None = None,
) -> None:
    formula_columns = formula_columns or {}
    html_parts = ['<div class="formula-table-wrap"><table class="formula-table"><thead><tr>']

    for column_name in visible_columns:
        html_parts.append(f"<th>{html.escape(str(column_name))}</th>")

    html_parts.append("</tr></thead><tbody>")

    for _, row in dataframe.iterrows():
        html_parts.append("<tr>")
        for column_name in visible_columns:
            value = row[column_name]
            tooltip_text = ""

            formula_column = formula_columns.get(column_name)
            if formula_column:
                tooltip_text = str(row.get(formula_column, "") or "")

            numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
            if pd.notna(numeric_value):
                display_value = format_number(numeric_value)
            else:
                display_value = html.escape(str("" if pd.isna(value) else value))

            title_attribute = f' title="{html.escape(tooltip_text)}"' if tooltip_text else ""
            html_parts.append(f"<td{title_attribute}>{display_value}</td>")
        html_parts.append("</tr>")

    html_parts.append("</tbody></table></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)
