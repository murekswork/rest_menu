import gspread
from gspread.client import Client
from typing import Optional


class SheetParsingInterface:

    def __init__(self):
        self.sheet_access: Optional[Client] = None

    async def authenticate(self, creds_file_path: str) -> gspread.client.Client:
        """Method to authenticate with credentials from file"""
        self.sheet_access = gspread.service_account(filename=creds_file_path)
        return self.sheet_access

    async def parse_sheet(self, url: str) -> list[list]:
        """Method to parse the sheet"""
        sheet = self.sheet_access.open_by_url(url)
        worksheet = sheet.get_worksheet(0)
        sheet_data = worksheet.get_all_values()
        return sheet_data
