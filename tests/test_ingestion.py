import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook

from ingest_portfolio import ingest


class TestExcelIngestion(unittest.TestCase):

    def test_missing_required_column(self):
        source = Path(__file__).resolve().parent.parent / "portfolio_week_1.xlsx"

        with TemporaryDirectory() as folder:
            test_file = Path(folder) / "invalid_portfolio.xlsx"

            workbook = load_workbook(source)
            sheet = workbook["Initiatives"]

            # Remove a required column header
            for cell in sheet[1]:
                if cell.value == "initiative_id":
                    cell.value = None
                    break

            workbook.save(test_file)

            # Verify ingestion rejects the invalid workbook
            with self.assertRaises(ValueError):
                ingest(test_file)

    def test_duplicate_initiative_id(self):
        source = Path(__file__).resolve().parent.parent / "portfolio_week_1.xlsx"

        with TemporaryDirectory() as folder:
            test_file = Path(folder) / "duplicate_portfolio.xlsx"

            workbook = load_workbook(source)
            sheet = workbook["Initiatives"]

            headers = [cell.value for cell in sheet[1]]
            id_column = headers.index("initiative_id") + 1

            # Make two initiatives share the same ID
            sheet.cell(row=3, column=id_column).value = sheet.cell(
                row=2, column=id_column
            ).value

            workbook.save(test_file)

            with self.assertRaises(ValueError):
                ingest(test_file)

    def test_invalid_dependency(self):
        source = Path(__file__).resolve().parent.parent / "portfolio_week_1.xlsx"

        with TemporaryDirectory() as folder:
            test_file = Path(folder) / "invalid_dependency.xlsx"

            workbook = load_workbook(source)
            sheet = workbook["Dependencies"]

            headers = [cell.value for cell in sheet[1]]
            dependency_column = headers.index("depends_on_initiative_id") + 1

            # Reference an initiative that does not exist
            sheet.cell(row=2, column=dependency_column).value = "PAY-99"

            workbook.save(test_file)

            with self.assertRaises(ValueError):
                ingest(test_file)