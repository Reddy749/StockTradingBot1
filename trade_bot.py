import asyncio
import logging
import json
import os
import pandas as pd
import yfinance as yf
import talib
import requests
from datetime import datetime, time
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackContext

# Configure logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Telegram Bot Token
BOT_TOKEN = "8037887985:AAGSBvWLulEfB2lFUKe2KjQH_jzdgTgqFr8
"

# Load or initialize portfolio
PORTFOLIO_FILE = "portfolio.json"
if os.path.exists(PORTFOLIO_FILE):
    with open(PORTFOLIO_FILE, "r") as file:
        portfolio = json.load(file)
else:
    portfolio = {}

# Function to check if the market is open
def is_market_open():
    now = datetime.now()
    current_time = now.time()
    market_start = time(9, 15)
    market_end = time(15, 30)
    return now.weekday() < 5 and market_start <= current_time <= market_end

# Function to fetch NSE and BSE symbols
def fetch_stock_symbols():
    # Fetch NSE symbols
    nse_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(nse_url, headers=headers)
    nse_symbols = []
    if response.status_code == 200:
        data = response.json()
        nse_symbols = [item['symbol'] + ".NS" for item in data['data']]

    # Fetch BSE symbols
    bse_url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_{}.zip".format(datetime.now().strftime("%d%m%y"))
    response = requests.get(bse_url, headers=headers)
    bse_symbols = []
    if response.status_code == 200:
        with open("bse_data.zip", "wb") as file:
            file.write(response.content)
        # Extract and read the CSV file from the ZIP archive
        # (Implementation depends on the structure of the ZIP file)

    return nse_symbols, bse_symbols

# Function to fetch recent news for a stock
def fetch_recent_news(symbol):
    search_url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey=YOUR_NEWSAPI_KEY"
    response = requests.get(search_url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        if articles:
            return articles[0]["title"]
    return None

# Function to calculate stop loss and target prices
def calculate_trade_levels(entry_price):
    stop_loss = entry_price * 0.98  # 2% below entry
    target = entry_price * 1.05     # 5% above entry
    return round(stop_loss, 2), round(target, 2)

# Function to scan for trade signals
async def scan_for_signals(update: Update, context: CallbackContext):
    if not is_market_open():
        await update.message.reply_text("The market is currently closed. Signals are generated only during market hours.")
        return

    nse_symbols, bse_symbols = fetch_stock_symbols()
    all_symbols = nse_symbols + bse_symbols

    for symbol in all_symbols:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="15d", interval="1d")
            if df.empty or len(df) < 15:
                continue

            close = df["Close"]
            rsi = talib.RSI(close, timeperiod=14)
            macd, macd_signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

            if rsi.iloc[-1] < 30 and macd.iloc[-1] > macd_signal.iloc[-1]:
                entry_price = close.iloc[-1]
                stop_loss, target = calculate_trade_levels(entry_price)
                news = fetch_recent_news(symbol)
                if news and any(neg_word in news.lower() for neg_word in ["fraud", "loss", "penalty"]):
                    continue

                signal = {
                    "symbol": symbol,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "target": target,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "news": news
                }
                portfolio[symbol] = signal
                with open(PORTFOLIO_FILE, "w") as file:
                    json.dump(portfolio, file)

                message = (
                    f"📈 *Trade Signal Detected!*\n\n"
                    f"*Symbol:* {symbol}\n"
                    f"*Entry Price:* ₹{entry_price:.2f}\n"
                    f"*Stop Loss:* ₹{stop_loss:.2f}\n"
                    f"*Target Price:* ₹{target:.2f}\n"
                    f"*Time:* {signal['timestamp']}\n"
                )
                if news:
                    message += f"*Recent News:* {news}\n"
                await update.message.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            logging.warning(f"Failed to process {symbol}: {e}")

# Command handlers
async def start(update: Update, context: CallbackContext):
    commands = (
        "/start - Start bot\n"
        "/menu - Show available commands\n"
        "/check_stock SYMBOL - Check stock data\n"
        "/get_signal - Manually fetch trade signals\n"
        "/portfolio - View your portfolio"
    )
    await update.message.reply_text(f"Welcome! Use the commands below:\n\n{commands}")

async def menu(update: Update, context: CallbackContext):
    commands = (
        "/check_stock SYMBOL - Get stock data\n"
        "/get_signal - Manually fetch trade signals\n"
        "/portfolio - View your portfolio"
    )
    await update.message.reply_text(f"Here are the available commands:\n\n{commands}")

async def check_stock(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /check_stock SYMBOL (e.g., /check_stock RELIANCE.NS)")
        return

    symbol = context.args[0]
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        await update.message.reply_text("Invalid stock symbol. Try again.")
    else:
        price = data["Close"].iloc[-1]
        await update.message.reply_text(f"📈 {symbol} latest price: ₹{price:.2f}")

async def get_signal(update: Update, context: CallbackContext):
    await scan_for_signals(update, context)

async def portfolio(update: Update, context: CallbackContext):
    if not portfolio:
        await update.message.reply_text("Your portfolio is currently empty.")
        return

    message = "📊 *Your Portfolio:*\n\n"
    for symbol, details in portfolio.items
::contentReference[oaicite:0]{index=0}
 
