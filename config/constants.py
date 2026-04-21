from pathlib import Path

APP_TITLE = "Vapi Spinning Manpower Engine"

INPUT_WORKBOOK_CANDIDATES = [
    Path("input/Spinning.xlsx"),
    Path("Spinning.xlsx"),
    Path(__file__).resolve().parents[1] / "input" / "Spinning.xlsx",
    Path("/mnt/data/Spinning.xlsx"),
]

OUTPUT_WORKBOOK_CANDIDATES = [
    Path("output/Spinning_working.xlsx"),
    Path(__file__).resolve().parents[1] / "output" / "Spinning_working.xlsx",
]

DEFAULT_OUTPUT_WORKBOOK_PATH = OUTPUT_WORKBOOK_CANDIDATES[0]

MASTER_SHEET_NAME = "Spinning"
TFO_SHEET_NAME = "TFO"

MASTER_COLUMNS = [
    "Location",
    "Business",
    "Section",
    "Sr_No",
    "Dept_Machine_Name",
    "Designation",
    "Machine_Count",
    "Workload",
    "Formulas",
    "BE_Scientific_Manpower",
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

MAIN_VIEW_COLUMNS = [
    "Section",
    "Dept_Machine_Name",
    "Designation",
    "BE_Final_Manpower",
]

SECTION_SUMMARY_COLUMNS = [
    "Section",
    "Machine_Count",
    "BE_Final_Manpower",
]

EDITOR_COLUMNS = [
    "Section",
    "Dept_Machine_Name",
    "Designation",
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

EDITABLE_NUMERIC_COLUMNS = [
    "Contractors",
    "Company_Associate",
    "BE_Final_Manpower",
    "General_Shift",
    "Shift_A",
    "Shift_B",
    "Shift_C",
    "Reliever",
]

TEXT_COLUMNS = [
    "Location",
    "Business",
    "Section",
    "Dept_Machine_Name",
    "Designation",
    "Workload",
    "Formulas",
    "Operator_Type",
    "Remarks",
]

NUMERIC_COLUMNS = [
    "Sr_No",
    "Machine_Count",
    "BE_Scientific_Manpower",
    "Contractors",
    "Company_Associate",
    "BE_Final_Manpower",
    "General_Shift",
    "Shift_A",
    "Shift_B",
    "Shift_C",
    "Reliever",
]

TFO_INPUT_COLUMNS = [
    "Count",
    "Customer",
    "Count2",
    "Speed",
    "TPI",
    "Utilization",
    "Efficiency",
    "Production Required / day Kgs",
    "mpm",
    "Eff",
]

TFO_PRODUCTION_DISPLAY_COLUMNS = [
    "Count",
    "Customer",
    "Count2",
    "Speed",
    "TPI",
    "Utilization",
    "Efficiency",
    "Production Required / day Kgs",
    "Production Required / Month Kgs",
    "Production per Drum/day",
    "No. of Drums Required",
    "TFO Reqd./ Shift",
    "mpm",
    "Eff",
    "kgs/drum/day",
    "No. of Drums (A/W) Reqd.",
    "Assembly Winding Reqd./ Shift",
]

TFO_MANPOWER_DISPLAY_COLUMNS = [
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

OPERATOR_TYPE_OPTIONS = ["", "Direct", "Indirect"]

SPECIAL_TFO_COUNT = "4/2/6 K"
DEFAULT_TFO_DIVISOR = 240.0
SPECIAL_TFO_DIVISOR = 80.0
DEFAULT_MACHINE_DIVISOR = 72.0

TFO_INPUT_START_ROW = 2
TFO_INPUT_END_ROW = 19
TFO_OUTPUT_START_ROW = 23

SUCCESS_MESSAGE_KEY = "freeze_success_message"
WORKBOOK_PATH_KEY = "workbook_path"
MASTER_DATA_KEY = "master_df"
MASTER_SOURCE_KEY = "master_source_df"
TFO_INPUT_DATA_KEY = "tfo_input_df"
TFO_PRODUCTION_DATA_KEY = "tfo_production_df"
TFO_MANPOWER_DATA_KEY = "tfo_manpower_df"
SECTION_ORDER_KEY = "section_order"
