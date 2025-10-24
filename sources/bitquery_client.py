
import os, requests

BITQUERY_ENDPOINT = os.getenv("BITQUERY_ENDPOINT", "https://graphql.bitquery.io")
BITQUERY_API_KEY = os.getenv("BITQUERY_API_KEY", "").strip()
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))

HEADERS = {"Content-Type": "application/json"}
if BITQUERY_API_KEY:
    HEADERS["X-API-KEY"] = BITQUERY_API_KEY

QUERY_V2 = """
{
  EVM(network: ethereum, dataset: realtime) {
    BalanceUpdates(
      limit: {count: %d}
      orderBy: {descendingByField: "balance"}
      where: {Currency: {Symbol: {is: "ETH"}}}
    ) {
      BalanceUpdate { Address }
      balance: sum(of: BalanceUpdate_BalanceAfter)
    }
  }
}
"""

QUERY_V1 = """
{
  ethereum(network: ethereum) {
    address(
      limit: %d
      orderBy: balance
      balances: {currency: {is: "ETH"}}
    ) {
      address
      annotation
      balances { currency { symbol } value }
    }
  }
}
"""

class BitqueryClient:
    def __init__(self):
        self.session = requests.Session()

    def available(self):
        return bool(BITQUERY_API_KEY)

    def top_eth_holders(self, limit=200):
        if not self.available():
            raise RuntimeError("Bitquery API key is missing")

        # Try V2
        try:
            payload = {"query": QUERY_V2 % limit}
            r = self.session.post(BITQUERY_ENDPOINT, json=payload, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            nodes = data.get("data", {}).get("EVM", {}).get("BalanceUpdates", [])
            out = []
            for i, n in enumerate(nodes, start=1):
                addr = (n.get("BalanceUpdate") or {}).get("Address")
                bal = n.get("balance")
                if addr and bal is not None:
                    out.append({"rank": i, "address": addr, "balance_eth": float(bal), "label": None})
            if out:
                return out
        except Exception:
            pass

        # Fallback V1
        payload = {"query": QUERY_V1 % limit}
        r = self.session.post(BITQUERY_ENDPOINT, json=payload, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        addrs = data.get("data", {}).get("ethereum", {}).get("address", [])
        out = []
        for i, a in enumerate(addrs, start=1):
            addr = a.get("address")
            label = a.get("annotation")
            eth_bal = None
            for b in a.get("balances", []):
                if b.get("currency", {}).get("symbol") == "ETH":
                    eth_bal = b.get("value")
                    break
            if addr and eth_bal is not None:
                out.append({"rank": i, "address": addr, "balance_eth": float(eth_bal), "label": label})
        if not out:
            raise RuntimeError("Bitquery returned no data (check API key/plan)")
        return out
