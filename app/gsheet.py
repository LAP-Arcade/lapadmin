import gspread

is_ready = False
try:
    gc = gspread.service_account(filename="keys/google.json")
    is_ready = True
except FileNotFoundError as e:
    msg = f"File not found: {e}"
    msg += "\nImporting from Google Sheets will not work."
    print(msg)

    class gc:
        def open(self, *args, **kwargs):
            raise ValueError(msg)
