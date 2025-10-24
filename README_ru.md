
# Телеграм‑бот: Топ‑200 кошельков по балансу ETH

Команда **/topeth** присылает список из 200 адресов с наибольшим количеством ETH «на сейчас». 
Основной источник — **Bitquery GraphQL API** (нужен бесплатный ключ). Резерв — **Etherscan Top Accounts** (парсинг таблиц).

## Установка
```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # заполните TELEGRAM_BOT_TOKEN, BITQUERY_API_KEY
python bot.py
```

## Замечания
- У разных источников методики учёта могут отличаться (биржевые кошельки и т.п.).
- При парсинге веб‑страниц соблюдайте условия использования сайтов; предусмотрены мягкие задержки.

