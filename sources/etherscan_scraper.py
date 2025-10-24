
import time, requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 25
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ETH-Top200-Bot/1.0)"}
BASE = "https://etherscan.io/accounts"

def _parse_table(html: str):
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    rows = []
    if not table:
        return rows
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue
        rank_txt = tds[0].get_text(strip=True).replace(",", "")
        addr_link = tds[1].find("a", href=True)
        address = addr_link.get("href", "").split("/")[-1] if addr_link else tds[1].get_text(strip=True)
        label = tds[2].get_text(strip=True) or None
        balance_txt = tds[3].get_text(strip=True).split(" ")[0].replace(",", "")
        try:
            rank = int(rank_txt)
            balance_eth = float(balance_txt)
        except Exception:
            continue
        rows.append({"rank": rank, "address": address, "label": label if label else None, "balance_eth": balance_eth})
    return rows

def fetch_top(limit: int = 200, delay_sec: float = 1.5):
    results = []
    page = 1
    session = requests.Session()
    while len(results) < limit and page < 500:
        url = BASE + (f"?p={page}" if page > 1 else "")
        r = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        chunk = _parse_table(r.text)
        if not chunk:
            break
        results.extend(chunk)
        page += 1
        time.sleep(delay_sec)
    results = sorted(results, key=lambda x: x["rank"])[:limit]
    for i, row in enumerate(results, start=1):
        row["rank"] = i
    return results
