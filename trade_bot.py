import logging
import yfinance as yf
import requests
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Replace with your actual Telegram bot token
BOT_TOKEN = "8037887985:AAGSBvWLulEfB2lFUKe2KjQH_jzdgTgqFr8
"

# Render Webhook URL (Replace with your Render deployment URL)
WEBHOOK_URL = "https://your-render-app-url.com/webhook"

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch stock data
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        latest_price = data["Close"].iloc[-1]
        return latest_price
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return None

# Fetch latest market news (Moneycontrol API)
def get_market_news():
    try:
        response = requests.get("https://newsapi.org/v2/top-headlines?category=business&apiKey=YOUR_NEWSAPI_KEY")
        news = response.json()
        articles = news["articles"][:3]  # Get top 3 news headlines
        news_text = "\n\n".join([f"📰 {article['title']}" for article in articles])
        return news_text
    except Exception as e:
        logger.error(f"Error fetching market news: {e}")
        return "No market news available."

# AI-based trade signal generation
def generate_trade_signal(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        
        # Get latest close price
        close_price = data["Close"].iloc[-1]

        # Generate simple trade signals
        buy_price = close_price * 1.01
        target_price = buy_price * 1.02
        stop_loss = close_price * 0.98

        return f"📊 Signal for {symbol}:\n🔹 Buy above: ₹{buy_price:.2f}\n🎯 Target: ₹{target_price:.2f}\n🛑 Stop Loss: ₹{stop_loss:.2f}"
    except Exception as e:
        logger.error(f"Error generating trade signal for {symbol}: {e}")
        return None

# Start command
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔍 Scan Market", callback_data='scan')],
        [InlineKeyboardButton("📈 Portfolio", callback_data='portfolio')],
        [InlineKeyboardButton("📰 Market News", callback_data='news')],
        [InlineKeyboardButton("⚡ Manual Signal", callback_data='manual_signal')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to Stock Trading Bot! Choose an option:", reply_markup=reply_markup)

# Button handler
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "scan":
        await query.edit_message_text("Scanning market for best trade signals...")

        # Fetch best trade signal (Replace with real scanning logic)
        stock_list = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFC.NS"]
        signals = [generate_trade_signal(stock) for stock in stock_list]

        signals_text = "\n\n".join(filter(None, signals))
        await query.message.reply_text(signals_text if signals_text else "No strong trade signals found today.")
    
    elif query.data == "portfolio":
        await query.edit_message_text("📊 Your past trades will be shown here soon!")
    
    elif query.data == "news":
        news = get_market_news()
        await query.message.reply_text(f"📰 Market News:\n\n{news}")

    elif query.data == "manual_signal":
        await query.edit_message_text("Send a stock symbol to generate a signal. Example: `/signal TCS.NS`")

# Manual Signal Command
async def manual_signal(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: `/signal SYMBOL` (e.g., `/signal TCS.NS`)")
        return
    
    symbol = context.args[0]
    signal = generate_trade_signal(symbol)
    
    if signal:
        await update.message.reply_text(signal)
    else:
        await update.message.reply_text("Could not generate signal. Try another stock.")

# Webhook setup
async def set_webhook():
    app = Application.builder().token(BOT_TOKEN).build()
    await app.bot.set_webhook(WEBHOOK_URL)

# Main function
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Set Webhook
    await set_webhook()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", manual_signal))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Set bot commands
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("signal", "Generate a manual trade signal"),
    ]
    await app.bot.set_my_commands(commands)

    # Start webhook listener
    await app.run_webhook(listen="0.0.0.0", port=8443, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
