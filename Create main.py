import requests
import time
import datetime
from telegram import Bot

# === CONFIGURATION ===
BOT_TOKEN = "7548394848:AAGj4OIzUqXWrUmxv9D05Oa4tTr14hmuAUo"
CHAT_ID = "niftysuggest_bot"

SYMBOL = "^NSEI"  # Nifty 50 symbol for Yahoo Finance
INTERVAL = 60 * 60  # Run every 1 hour

bot = Bot(token=BOT_TOKEN)

def get_nifty_price_history():
    end = int(time.time())
    start = end - (300 * 86400)  # 300 days back
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?symbol={SYMBOL}&period1={start}&period2={end}&interval=1d"

    response = requests.get(url)
    data = response.json()

    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    timestamps = data["chart"]["result"][0]["timestamp"]
    return closes, timestamps

def calculate_dma(closes, days):
    dma = []
    for i in range(len(closes)):
        if i < days:
            dma.append(None)
        else:
            dma.append(sum(closes[i - days:i]) / days)
    return dma

def send_telegram_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    print("Bot started...")

    while True:
        try:
            closes, timestamps = get_nifty_price_history()

            # Remove None values for clean list
            prices = [p for p in closes if p is not None]

            dma_50 = calculate_dma(prices, 50)
            dma_200 = calculate_dma(prices, 200)

            latest_price = prices[-1]
            latest_dma_50 = dma_50[-1]
            latest_dma_200 = dma_200[-1]

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            if latest_price > latest_dma_50 and latest_price > latest_dma_200:
                message = f"📈 *BUY SIGNAL - NIFTY*\n\n" \
                          f"Price: ₹{latest_price:.2f}\n" \
                          f"50 DMA: ₹{latest_dma_50:.2f}\n" \
                          f"200 DMA: ₹{latest_dma_200:.2f}\n" \
                          f"✅ Above both DMA\nTime: {now}"
                send_telegram_alert(message)

            elif latest_price < latest_dma_50 and latest_price < latest_dma_200:
                message = f"📉 *SELL SIGNAL - NIFTY*\n\n" \
                          f"Price: ₹{latest_price:.2f}\n" \
                          f"50 DMA: ₹{latest_dma_50:.2f}\n" \
                          f"200 DMA: ₹{latest_dma_200:.2f}\n" \
                          f"⚠️ Below both DMA\nTime: {now}"
                send_telegram_alert(message)

            else:
                print(f"{now} — No strong signal.")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
