
import os, logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sources.bitquery_client import BitqueryClient
from sources.etherscan_scraper import fetch_top
from utils import format_top_list

load_dotenv()
logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("eth_top200_bot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is missing")

bitq = BitqueryClient()
last_source = {"name": None}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Команда /topeth пришлёт Топ‑200 адресов с наибольшим балансом ETH.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/topeth — Топ‑200 по ETH\n/source — какой источник использован")

async def source_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Текущий источник: {last_source.get('name') or '—'}")

async def topeth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ищу Топ‑200 ETH адресов…")
    rows = []
    source_name = None
    if bitq.available():
        try:
            rows = bitq.top_eth_holders(limit=200)
            source_name = "Bitquery API"
        except Exception as e:
            log.warning("Bitquery failed: %s", e)
    if not rows:
        try:
            rows = fetch_top(limit=200)
            source_name = "Etherscan (парсинг)"
        except Exception as e:
            log.exception("Etherscan fallback failed: %s", e)
            await update.message.reply_text("Не удалось получить данные. Попробуйте позже.")
            return
    last_source["name"] = source_name
    chunks = format_top_list(rows, header=f"Топ‑200 адресов по балансу ETH\nИсточник: {source_name}")
    for part in chunks:
        await update.message.reply_text(part)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("source", source_cmd))
    app.add_handler(CommandHandler("topeth", topeth))
    log.info("Bot started")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
