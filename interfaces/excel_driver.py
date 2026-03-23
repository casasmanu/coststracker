import os
import logging
import datetime
from openpyxl import Workbook, load_workbook

logger = logging.getLogger(__name__)

VARIABLE_EXPENSES_SHEET = "VariableExpenses"
LEGACY_VARIABLE_EXPENSES_SHEET = "GastosVarios"


def _resolve_variable_expenses_sheet(workbook, requested_sheet_name: str) -> str:
    """Map variable-expenses sheet to legacy name when needed."""
    if requested_sheet_name != VARIABLE_EXPENSES_SHEET:
        return requested_sheet_name

    if VARIABLE_EXPENSES_SHEET in workbook.sheetnames:
        return VARIABLE_EXPENSES_SHEET

    if LEGACY_VARIABLE_EXPENSES_SHEET in workbook.sheetnames:
        return LEGACY_VARIABLE_EXPENSES_SHEET

    return VARIABLE_EXPENSES_SHEET


def _ensure_excel(path: str):
    """Create Excel file if it does not exist"""
    if not os.path.exists(path):
        wb = Workbook()
        wb.save(path)
        wb.close()
        logger.info(f"Excel file created at {path}")


def _ensure_sheet(path: str, sheet_name: str, columns: list):
    """Create sheet with headers if it does not exist"""
    wb = load_workbook(path)

    if sheet_name not in wb.sheetnames:
        ws = wb.create_sheet(sheet_name)
        ws.append(columns)
        wb.save(path)
        logger.info(f"Sheet '{sheet_name}' created")

    wb.close()


def update_excel(path, sheet_name, sheet_columns, sheet_data):
    """
    Append a row to a sheet.
    Automatically creates file and sheet if needed.
    """

    try:

        _ensure_excel(path)

        wb = load_workbook(path)
        resolved_sheet_name = _resolve_variable_expenses_sheet(wb, sheet_name)
        wb.close()

        columns = sheet_columns.copy()

        if resolved_sheet_name in (VARIABLE_EXPENSES_SHEET, LEGACY_VARIABLE_EXPENSES_SHEET):
            # Keep month explicitly in column F, leaving column E available.
            month_column = "Mes" if resolved_sheet_name == LEGACY_VARIABLE_EXPENSES_SHEET else "Month"
            columns = ["Date"] + columns + ["", month_column]

        _ensure_sheet(path, resolved_sheet_name, columns)

        wb = load_workbook(path)
        ws = wb[resolved_sheet_name]

        row = sheet_data.copy()

        if resolved_sheet_name in (VARIABLE_EXPENSES_SHEET, LEGACY_VARIABLE_EXPENSES_SHEET):
            today = datetime.date.today()
            month_names = {
                1: "JANUARY",
                2: "FEBRUARY",
                3: "MARCH",
                4: "APRIL",
                5: "MAY",
                6: "JUNE",
                7: "JULY",
                8: "AUGUST",
                9: "SEPTEMBER",
                10: "OCTOBER",
                11: "NOVEMBER",
                12: "DECEMBER",
            }
            month = month_names[today.month]
            # Row layout for VariableExpenses: A=date, B-D=user data, E=empty, F=month.
            row = [today] + row + ["", month]

        ws.append(row)

        wb.save(path)
        wb.close()

        logger.info(f"Added row to {resolved_sheet_name}: {row}")

        return True

    except Exception as e:
        logger.error(f"Error updating Excel: {e}")
        return False


def read_data(path, sheet_name):
    """Return sheet data formatted for Telegram"""

    try:

        if not os.path.exists(path):
            return "No Excel file found."

        wb = load_workbook(path)

        if sheet_name not in wb.sheetnames:
            return f"No data for {sheet_name}"

        ws = wb[sheet_name]

        rows = list(ws.values)

        wb.close()

        if len(rows) <= 1:
            return "No data yet."

        data_rows = rows[1:]

        output = f"{sheet_name} prices\n\n"

        for row in data_rows:
            row_text = " | ".join(str(x) for x in row)
            output += row_text + "\n"

        return output

    except Exception as e:
        logger.error(f"Error reading Excel: {e}")
        return "Error reading Excel."


def get_last_expenses(path: str, sheet_name: str = "VariableExpenses", n: int = 5):
    """Return the last n expense rows from the sheet as a list of dicts."""
    try:
        if not os.path.exists(path):
            return []

        wb = load_workbook(path)

        resolved_sheet_name = _resolve_variable_expenses_sheet(wb, sheet_name)

        if resolved_sheet_name not in wb.sheetnames:
            wb.close()
            return []

        ws = wb[resolved_sheet_name]
        rows = list(ws.values)
        wb.close()

        if len(rows) <= 1:
            return []

        header = rows[0]
        data_rows = rows[1:]
        last_rows = data_rows[-n:]

        result = []
        for row in last_rows:
            result.append(dict(zip(header, row)))

        return result

    except Exception as e:
        logger.error(f"Error reading last expenses: {e}")
        return []