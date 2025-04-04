
import logging
import yfinance as yf
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_stock_data(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period='1d')
        if data.empty:
            return None
        latest_price = data['Close'].iloc[-1]
        return latest_price
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Stock Signals", callback_data='signals')],
        [InlineKeyboardButton("Portfolio", callback_data='portfolio')],
        [InlineKeyboardButton("Market News", callback_data='news')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📊 Welcome to Stock Trading Bot!\nChoose an option:", reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "signals":
        await query.edit_message_text("📈 Fetching today's best stock signals...")
        signal = "📌 NSE: RELIANCE - Buy above ₹2500 (Target: ₹2550, SL: ₹2480)"
        await query.message.reply_text(signal)
    elif query.data == "portfolio":
        await query.edit_message_text("📁 Portfolio tracking coming soon!")
    elif query.data == "news":
        await query.edit_message_text("📰 Market news feature coming soon!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol = update.message.text.upper().strip()
    price = get_stock_data(symbol)
    if price:
        await update.message.reply_text(f"💹 Current price of {symbol}: ₹{price:.2f}")
    else:
        await update.message.reply_text("❌ Could not fetch data. Please check the stock symbol.")

def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(lambda update, context: logger.error(f"Update {update} caused error {context.error}"))
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
