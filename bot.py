# ATILATRADER HFT PRO – KUCOIN 24/7 (RAILWAY / RENDER / REPLIT)
import ccxt
import asyncio
import time
import os
from telegram import Bot
from datetime import datetime
import threading

# ==== TUS LLAVES (Railway las lee como variables de entorno) ====
KUCOIN_KEY         = os.getenv("KUCOIN_KEY")
KUCOIN_SECRET      = os.getenv("KUCOIN_SECRET")
KUCOIN_PASSPHRASE  = os.getenv("KUCOIN_PASSPHRASE")
TELEGRAM_TOKEN     = os.getenv("TELEGRAM_TOKEN")
CHAT_ID            = os.getenv("CHAT_ID")

# Telegram
bot = Bot(token=TELEGRAM_TOKEN)
async def send(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg[:4096])
    except Exception as e:
        print("Error Telegram:", e)

# KuCoin
exchange = ccxt.kucoin({
    'apiKey': KUCOIN_KEY,
    'secret': KUCOIN_SECRET,
    'password': KUCOIN_PASSPHRASE,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# 30 pares USDC
CRYPTOS = [
    'BTC-USDC','ETH-USDC','SOL-USDC','ADA-USDC','XRP-USDC','DOGE-USDC','DOT-USDC',
    'AVAX-USDC','MATIC-USDC','LINK-USDC','LTC-USDC','BCH-USDC','UNI-USDC','FIL-USDC',
    'AAVE-USDC','ATOM-USDC','VET-USDC','TRX-USDC','HBAR-USDC','ICP-USDC','NEAR-USDC',
    'ALGO-USDC','EGLD-USDC','MANA-USDC','SAND-USDC','CHZ-USDC','GALA-USDC','AXS-USDC',
    'KSM-USDC','ENJ-USDC'
]

positions = {}
loss_streak = 0

def trading_loop():
    global loss_streak
    print("ATILATRADER HFT PRO – INICIADO EN RAILWAY")
    asyncio.run(send("ATILATRADER KUCOIN INICIADO\n30 pares | 24/7 | Railway"))
    
    while True:
        for sym in CRYPTOS:
            try:
                ticker = exchange.fetch_ticker(sym)
                price = ticker['last']
                ob = exchange.fetch_order_book(sym, limit=5)
                bids_vol = sum([x[1] for x in ob['bids']])
                asks_vol = sum([x[1] for x in ob['asks']])
                obi = (bids_vol - asks_vol) / (bids_vol + asks_vol + 1e-8)

                # ENTRADA ($10 USDC)
                if sym not in positions and obi > 0.38:
                    amount = 10 / price
                    exchange.create_market_buy_order(sym, amount)
                    positions[sym] = {'entry': price, 'peak': price}
                    asyncio.run(send(f"ENTRADA {sym.split('-')[0]}\n${price:.4f} | $10 USDC"))

                # GESTIÓN
                if sym in positions:
                    pos = positions[sym]
                    pos['peak'] = max(pos['peak'], price)

                    sold = False
                    if price < pos['entry'] * 0.985:  # Stop-Loss 1.5%
                        sold = True
                        loss_streak += 1
                    elif price > pos['entry'] * 1.008:  # Take-Profit 0.8%
                        sold = True
                        loss_streak = 0
                    elif price < pos['peak'] * 0.993:  # Trailing 0.7%
                        sold = True
                        loss_streak = 0

                    if sold:
                        amount = positions[sym]['amount'] if 'amount' in positions[sym] else 10/pos['entry']
                        exchange.create_market_sell_order(sym, amount)
                        profit = (price - pos['entry']) * amount
                        asyncio.run(send(f"{'STOP-LOSS' if profit<0 else 'TAKE PROFIT'} {sym.split('-')[0]}\n+${profit:.3f}"))
                        del positions[sym]

            except Exception as e:
                if "nonce" not in str(e) and "symbol" not in str(e):
                    print(f"Error {sym}: {e}")
            time.sleep(0.08)
        time.sleep(0.3)

# INICIAR BOT
threading.Thread(target=trading_loop, daemon=True).start()

# Mantener vivo + dashboard
while True:
    print(f"Bot vivo | {datetime.now().strftime('%H:%M:%S')} | Posiciones: {len(positions)}")
    time.sleep(30)
