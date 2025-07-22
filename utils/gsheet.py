# utils/gsheet.py ✅
import os
import gspread
import json
from google.oauth2.service_account import Credentials  # ✅ Ganti oauth2client (deprecated)

# Ambil dari environment variable
json_creds = os.environ.get("GOOGLE_CREDS")
info = json.loads(json_creds)

# Scope akses
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)

spreadsheet_id = '1Og7KigH3QL3eTvLLMrIXMq7gaUzqFaw7B1RBL4aMHTo'

def get_sheet(sheet_name="Halaqah Umar"):
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)
