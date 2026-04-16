import datetime
import os
import tempfile
import unittest

from openpyxl import Workbook

from interfaces.excel_driver import get_expenses_for_month, get_monthly_category_breakdown


class MonthlyInsightsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.excel_path = os.path.join(self.temp_dir.name, "expenses.xlsx")
        self._create_excel()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "VariableExpenses"
        ws.append(["Date", "Description", "Amount", "Extra", "", "Month"])
        ws.append([datetime.date(2026, 3, 3), "Coffee", 4.0, "food", "", "MARCH"])
        ws.append([datetime.date(2026, 3, 10), "Train", 18.0, "transport", "", "MARCH"])
        ws.append([datetime.date(2026, 3, 15), "Lunch", 12.0, "food", "", "MARCH"])
        ws.append([datetime.date(2026, 4, 2), "Movie", 10.0, "entertainment", "", "APRIL"])
        wb.save(self.excel_path)
        wb.close()

    def test_get_expenses_for_month_filters_by_month_and_year(self):
        expenses = get_expenses_for_month(path=self.excel_path, year=2026, month=3)
        self.assertEqual(len(expenses), 3)
        self.assertEqual(expenses[0]["Description"], "Coffee")

    def test_get_monthly_category_breakdown_aggregates_amounts(self):
        breakdown = get_monthly_category_breakdown(path=self.excel_path, year=2026, month=3)
        totals = dict(breakdown)
        self.assertEqual(totals["food"], 16.0)
        self.assertEqual(totals["transport"], 18.0)


if __name__ == "__main__":
    unittest.main()
