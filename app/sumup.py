import json
import urllib.parse
import urllib.request
from typing import Optional

from pydantic import BaseModel, Field

from app import app

_ENTRY_MODE_FR: dict[str, str] = {
    "none": "espèces",
    "contactless": "sans contact",
    "chip": "puce",
    "magstripe": "bande magnétique",
    "magstripe_fallback": "bande magnétique",
    "manual_entry": "saisie manuelle",
    "customer_entry": "saisie client",
}


class Transaction(BaseModel):
    transaction_code: str
    amount: float
    currency: str
    timestamp: str
    status: str
    payment_type: Optional[str] = None
    entry_mode: Optional[str] = None
    card_type: Optional[str] = None
    user: Optional[str] = None

    @property
    def moyen(self) -> str:
        raw = (self.entry_mode or "").lower()
        return _ENTRY_MODE_FR.get(
            raw, self.entry_mode or self.payment_type or "—"
        )

    class Config:
        extra = "allow"


def _get(path: str, params: dict = None) -> dict:
    api_key = app.config.get("SUMUP_API_KEY")
    if not api_key:
        raise RuntimeError("SUMUP_API_KEY is not configured")
    url = f"https://api.sumup.com{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


_merchant_code_cache: str | None = None


def get_merchant_code() -> str:
    global _merchant_code_cache
    if _merchant_code_cache is None:
        data = _get("/v0.1/me/merchant-profile")
        _merchant_code_cache = data["merchant_code"]
    return _merchant_code_cache


def list_transactions(
    limit: int = 20, oldest_ref: str = None, newest_ref: str = None
) -> tuple[list[Transaction], dict]:
    merchant_code = get_merchant_code()
    params = {"limit": limit, "order": "descending", "statuses[]": "SUCCESSFUL"}
    if oldest_ref:
        params["oldest_ref"] = oldest_ref
    if newest_ref:
        params["newest_ref"] = newest_ref
    data = _get(f"/v2.1/merchants/{merchant_code}/transactions/history", params)
    transactions = [Transaction(**item) for item in data.get("items", [])]
    links = {}
    for lnk in data.get("links", []):
        qs = urllib.parse.parse_qs(lnk.get("href", ""))
        if lnk["rel"] == "next" and "newest_ref" in qs:
            links["next_newest_ref"] = qs["newest_ref"][0]
        elif lnk["rel"] == "prev" and "oldest_ref" in qs:
            links["prev_oldest_ref"] = qs["oldest_ref"][0]
    return transactions, links
