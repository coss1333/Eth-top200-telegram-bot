
def format_top_list(rows, header: str):
    lines = [header]
    for r in rows:
        label = f" — {r['label']}" if r.get("label") else ""
        lines.append(f"{r['rank']:>3}. {r['address']}{label}\n     {r['balance_eth']:,.6f} ETH")
    chunks, cur = [], ""
    for line in lines:
        if len(cur) + len(line) + 1 > 4000:
            chunks.append(cur.rstrip())
            cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur.rstrip())
    return chunks
