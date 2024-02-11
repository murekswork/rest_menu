import gspread


class SheetParsingInterface:

    def __init__(self):
        self.sheet_access = None
        self.sheet_url = None

    async def authenticate(self, creds_file_path: str):
        self.sheet_access = gspread.service_account(filename=creds_file_path)
        return self.sheet_access

    async def parse_sheet(self, url: str):
        sheet = self.sheet_access.open_by_url(url)
        worksheet = sheet.get_worksheet(0)
        sheet_data = worksheet.get_all_values()
        return sheet_data
