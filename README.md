# Vapi Spinning Manpower Engine

## File behavior

- `input/Spinning.xlsx` → original master file
- `output/Spinning_working.xlsx` → working saved file

## Load behavior

- If `output/Spinning_working.xlsx` exists, the app loads it.
- Otherwise, the app loads `input/Spinning.xlsx`.

## Save behavior

- **Freeze Changes** overwrites only `output/Spinning_working.xlsx`.
- `input/Spinning.xlsx` remains untouched.

## Reset behavior

- **Reset from Input** deletes the working file and reloads the original input workbook.
