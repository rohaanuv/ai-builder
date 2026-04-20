"""Extract text from CSV, Excel .xlsx, and legacy .xls."""

from typing import ClassVar

from ..common import FormatLoader


class SpreadsheetLoader(FormatLoader):
    """Load tabular files as newline-separated rows (tab-separated cells)."""

    name = "loader-spreadsheet"
    description = "Load CSV, XLSX, and XLS spreadsheets"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".csv", ".xlsx", ".xls")


tool = SpreadsheetLoader()
