import time

import gspread
from gspread.exceptions import APIError

MAX_RETRIES = 5


def _request_with_retry(request, self, method, endpoint, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return request(self, method, endpoint, *args, **kwargs)
        except APIError as e:
            if e.response.status_code != 429 or attempt == MAX_RETRIES - 1:
                raise
            wait = 32 * (2**attempt)
            print(f"Google Sheets API rate limited, retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("unreachable")


_original_request = gspread.http_client.HTTPClient.request
gspread.http_client.HTTPClient.request = lambda self, *a, **kw: (
    _request_with_retry(_original_request, self, *a, **kw)
)

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
