import functools
import json
import urllib.parse
import urllib.request

from pydantic import BaseModel

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


_CARD_LOGOS: dict[str, str] = {
    "VISA": "https://circuit.sumup.com/icons/v2/visa_32.svg",
    "VISA_VPAY": "https://upload.wikimedia.org/wikipedia/commons/e/ed/VPay_logo_2015.svg",
    "MASTERCARD": "https://circuit.sumup.com/icons/v2/mastercard_32.svg",
    "MAESTRO": "https://circuit.sumup.com/icons/v2/mastercard_32.svg",
}


class Transaction(BaseModel):
    id: str
    transaction_code: str
    amount: float
    currency: str
    timestamp: str
    status: str
    client_transaction_id: str
    product_summary: str | None = None
    payment_type: str | None = None
    entry_mode: str | None = None
    card_type: str | None = None
    user: str | None = None

    @property
    def card_logo_url(self) -> str | None:
        if self.card_type:
            return _CARD_LOGOS.get(self.card_type.upper())
        return None

    @property
    def moyen(self) -> str:
        raw = (self.entry_mode or "").lower()
        return _ENTRY_MODE_FR.get(
            raw, self.entry_mode or self.payment_type or "—"
        )

    @property
    def client_transaction_id_short(self) -> str:
        return self.client_transaction_id.split(":")[-2]

    @property
    def merchant_code(self) -> str:
        return self.client_transaction_id.split(":")[-3]

    class Config:
        extra = "allow"

    def model_post_init(self, __context):
        if self.product_summary in ("Custom amount", "Montant personnalisé"):
            self.product_summary = None


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


@functools.cache
def get_merchant_code() -> str:
    data = _get("/v0.1/me/merchant-profile")
    return data["merchant_code"]


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
