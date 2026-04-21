from __future__ import annotations

import streamlit as st



def apply_app_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #ffffff;
                color: #0f172a;
            }

            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            footer,
            #MainMenu {
                display: none !important;
            }

            .block-container {
                max-width: 1520px;
                padding-top: 0.75rem;
                padding-bottom: 2rem;
            }

            .app-title {
                color: #2563eb;
                font-size: 1.18rem;
                font-weight: 800;
                line-height: 1.2;
                margin-bottom: 0.75rem;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.45rem;
                border-bottom: 1px solid #dbeafe;
                padding-bottom: 0.4rem;
                margin-bottom: 0.55rem;
            }

            .stTabs [data-baseweb="tab"] {
                background: #ffffff;
                color: #1e3a8a;
                border: 1px solid #bfdbfe;
                border-radius: 999px;
                padding: 0.5rem 1rem;
                font-weight: 700;
            }

            .stTabs [aria-selected="true"] {
                background: #eff6ff !important;
                color: #1d4ed8 !important;
                border-color: #60a5fa !important;
                box-shadow: inset 0 3px 0 #2563eb;
            }

            .panel-title {
                color: #1e3a8a;
                font-size: 1.03rem;
                font-weight: 700;
                margin-top: 0.05rem;
                margin-bottom: 0.65rem;
            }

            .mini-title {
                color: #1e3a8a;
                font-size: 0.94rem;
                font-weight: 700;
                margin-top: 0.15rem;
                margin-bottom: 0.45rem;
            }

            .metric-card {
                background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 1rem 1.05rem;
                min-height: 124px;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
                position: relative;
                overflow: hidden;
                margin-bottom: 0.35rem;
            }

            .metric-card::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, #1d4ed8 0%, #38bdf8 100%);
            }

            .metric-card::after {
                content: "";
                position: absolute;
                top: -30px;
                right: -25px;
                width: 140px;
                height: 140px;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.18), transparent 68%);
                pointer-events: none;
            }

            .metric-label {
                color: #64748b;
                font-size: 0.8rem;
                font-weight: 800;
                letter-spacing: 0.02em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
                position: relative;
                z-index: 1;
            }

            .metric-value {
                color: #0f172a;
                font-size: 1.35rem;
                font-weight: 900;
                line-height: 1.08;
                position: relative;
                z-index: 1;
            }

            .metric-note {
                color: #64748b;
                font-size: 0.78rem;
                margin-top: 0.45rem;
                position: relative;
                z-index: 1;
            }

            .section-shell {
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 0.85rem 0.95rem 0.35rem 0.95rem;
                margin-bottom: 0.85rem;
                background: #ffffff;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            }

            .section-name {
                color: #1e3a8a;
                font-size: 0.98rem;
                font-weight: 700;
                margin-bottom: 0.55rem;
            }

            .formula-table-wrap {
                overflow-x: auto;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                margin-bottom: 0.9rem;
                background: #ffffff;
            }

            table.formula-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.87rem;
                background: #ffffff;
            }

            table.formula-table thead th {
                background: #eff6ff;
                color: #1e3a8a;
                text-align: left;
                padding: 10px 12px;
                border-bottom: 1px solid #dbeafe;
                white-space: nowrap;
            }

            table.formula-table tbody td {
                padding: 9px 12px;
                border-bottom: 1px solid #f1f5f9;
                white-space: nowrap;
                color: #0f172a;
                background: #ffffff;
            }

            table.formula-table tbody tr:hover {
                background: #f8fafc;
            }

            table.formula-table tbody tr:last-child td {
                background: #f8fafc;
                font-weight: 700;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stDataEditor"] {
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                overflow: hidden;
                background: #ffffff !important;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            }

            div[data-testid="stDataFrame"] * {
                color: #0f172a !important;
            }

            div[data-testid="stDataEditor"] * {
                color: #000000 !important;
            }

            div[data-testid="stDataEditor"] input,
            div[data-testid="stDataEditor"] textarea,
            div[data-testid="stDataEditor"] [role="gridcell"],
            div[data-testid="stDataEditor"] [data-testid="stWidgetLabel"] {
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
                background: #ffffff !important;
            }

            .freeze-wrap {
                margin-top: 1.15rem;
                padding-top: 0.8rem;
            }

            .stButton button,
            .stDownloadButton button {
                background: #2563eb;
                color: #ffffff;
                border: 1px solid #2563eb;
                border-radius: 12px;
                font-weight: 700;
                min-height: 44px;
            }

            .stButton button:hover,
            .stDownloadButton button:hover {
                background: #1d4ed8;
                border-color: #1d4ed8;
                color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
