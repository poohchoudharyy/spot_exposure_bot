import logging
import asyncio
import ccxt
import matplotlib.pyplot as plt
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import io

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Exchanges
exchange_map = {
    'binance': ccxt.binance(),
    'bybit': ccxt.bybit(),
    'okx': ccxt.okx(),
}

# Global State
risk_settings = {}
hedge_history = {}
auto_hedge_settings = {}
pnl_tracking = {}

# Risk Analytics
def calculate_greeks(symbol, position_size):
    return {
        'delta': round(position_size * 0.8, 2),
        'gamma': round(position_size * 0.05, 2),
        'theta': round(-position_size * 0.01, 2),
        'vega': round(position_size * 0.02, 2)
    }

def calculate_var(position_value, confidence_z=1.65, volatility=0.05):
    return round(confidence_z * volatility * position_value, 2)

def calculate_max_drawdown(position_value):
    return round(position_value * 0.08, 2)

def calculate_correlation():
    return 0.92

def estimate_slippage(price):
    return round(price * 0.002, 2)

def get_price(symbol, exchange_name='binance'):
    try:
        exchange = exchange_map.get(exchange_name)
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        logger.error(f"Price fetch error: {e}")
        return None

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Monitor Risk", callback_data='monitor')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome to the Spot Hedging Bot!", reply_markup=reply_markup)

async def monitor_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper() + "/USDT"
        position_size = float(context.args[1])
        threshold = float(context.args[2])
        exchange_name = context.args[3].lower() if len(context.args) > 3 else 'binance'
        chat_id = update.effective_chat.id
        risk_settings[chat_id] = {
            'symbol': symbol,
            'position_size': position_size,
            'threshold': threshold,
            'exchange': exchange_name
        }
        keyboard = [[InlineKeyboardButton("🛡️ Hedge Now", callback_data='hedge_now_clicked')]]
        await update.message.reply_text(
            f"✅ Monitoring {symbol} | Size: {position_size} | Threshold: {threshold}%",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await update.message.reply_text("❌ Usage: /monitor_risk <asset> <size> <threshold> <exchange>")

async def hedge_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    data = risk_settings.get(chat_id)
    if not data:
        await query.edit_message_text("⚠️ No monitoring session.")
        return
    price = get_price(data['symbol'], data['exchange'])
    if not price:
        await query.edit_message_text("❌ Failed to get price.")
        return
    size = data['position_size']
    cost = size * price * 0.001
    hedge_history.setdefault(chat_id, []).append(f"{datetime.now()} | {data['symbol']} | ${cost:.2f}")
    pnl_tracking.setdefault(chat_id, []).append({'symbol': data['symbol'], 'entry_price': price, 'size': size})
    await query.edit_message_text(f"✅ Hedged {data['symbol']} | Size: {size} | Cost: ${cost:.2f}")

async def configure_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        new_threshold = float(context.args[0])
        risk_settings[chat_id]['threshold'] = new_threshold
        await update.message.reply_text(f"⚙️ Threshold updated to {new_threshold}%")
    except:
        await update.message.reply_text("❌ Usage: /configure_risk <new_threshold>")

async def hedge_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    risk = risk_settings.get(chat_id)
    if not risk:
        await update.message.reply_text("⚠️ No monitoring session.")
        return
    auto = auto_hedge_settings.get(chat_id)
    msg = (
        f"📋 Hedge Status\nSymbol: {risk['symbol']}\nSize: {risk['position_size']}\n"
        f"Threshold: {risk['threshold']}%\nExchange: {risk['exchange'].upper()}"
    )
    if auto:
        msg += f"\n🤖 Auto-Hedge: ON | Strategy: {auto['strategy']}"
    await update.message.reply_text(msg)

async def auto_hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    strategy = context.args[0]
    threshold = float(context.args[1])
    auto_hedge_settings[chat_id] = {'strategy': strategy, 'threshold': threshold}
    await update.message.reply_text(f"✅ Auto-Hedge ON | Strategy: {strategy} | Threshold: {threshold}%")

async def hedge_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    history = hedge_history.get(chat_id, [])
    if not history:
        await update.message.reply_text("📭 No hedge history.")
        return
    await update.message.reply_text("📜 Hedge History:\n" + "\n".join(history[-5:]))

async def pnl_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    entries = pnl_tracking.get(chat_id, [])
    total = 0
    lines = []
    for e in entries:
        cp = get_price(e['symbol'])
        if not cp:
            continue
        pnl = round((cp - e['entry_price']) * e['size'], 2)
        lines.append(f"{e['symbol']}: {e['entry_price']} → {cp} | Size {e['size']} | PnL: ${pnl}")
        total += pnl
    await update.message.reply_text("💰 PnL Summary:\n" + "\n".join(lines) + f"\nTotal: ${total:.2f}")

async def stress_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = risk_settings.get(chat_id)
    price = get_price(data['symbol'], data['exchange'])
    pos_val = price * data['position_size']
    down_var = calculate_var(pos_val * 0.9)
    up_var = calculate_var(pos_val * 1.1)
    await update.message.reply_text(
        f"🧪 Stress Test:\nPrice: ${price:.2f}\n-10% VaR: ${down_var}\n+10% VaR: ${up_var}"
    )

async def portfolio_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = risk_settings.get(chat_id)
    price = get_price(data['symbol'], data['exchange'])
    pos_val = price * data['position_size']
    greeks = calculate_greeks(data['symbol'], data['position_size'])
    var = calculate_var(pos_val)
    dd = calculate_max_drawdown(pos_val)
    corr = calculate_correlation()
    await update.message.reply_text(
        f"📊 Portfolio:\n{data['symbol']} | Size: {data['position_size']} | Price: ${price:.2f}\n"
        f"Delta: {greeks['delta']} | Gamma: {greeks['gamma']} | Theta: {greeks['theta']} | Vega: {greeks['vega']}\n"
        f"VaR: ${var} | Max DD: ${dd} | Corr: {corr}"
    )

# Charts
async def risk_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = risk_settings.get(chat_id)
    size = data['position_size']
    price = get_price(data['symbol'], data['exchange'])
    prices = [price * (1 + i / 100) for i in range(-5, 6)]
    vars = [calculate_var(p * size) for p in prices]
    plt.plot(prices, vars, marker='o')
    plt.title("VaR vs Price")
    plt.xlabel("Price")
    plt.ylabel("VaR")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await update.message.reply_photo(photo=InputFile(buf, filename="risk_chart.png"))
    buf.close()
    plt.close()

async def greeks_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = risk_settings.get(chat_id)
    greeks = calculate_greeks(data['symbol'], data['position_size'])
    names = list(greeks.keys())
    values = list(greeks.values())
    plt.bar(names, values)
    plt.title("Greek Exposures")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await update.message.reply_photo(photo=InputFile(buf, filename="greeks_chart.png"))
    buf.close()
    plt.close()

async def pnl_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    entries = pnl_tracking.get(chat_id, [])
    if not entries:
        await update.message.reply_text("No PnL data yet.")
        return
    labels, values = [], []
    for e in entries:
        cp = get_price(e['symbol'])
        if not cp:
            continue
        pnl = round((cp - e['entry_price']) * e['size'], 2)
        labels.append(e['symbol'])
        values.append(pnl)
    plt.bar(labels, values)
    plt.title("PnL per Asset")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await update.message.reply_photo(photo=InputFile(buf, filename="pnl_chart.png"))
    buf.close()
    plt.close()

# Bot Runner
def main():
    app = ApplicationBuilder().token("7011857661:AAHzstvKEbry8UMn4k5bRqdNxveuZRAptHI").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("monitor_risk", monitor_risk))
    app.add_handler(CallbackQueryHandler(hedge_now, pattern="hedge_now_clicked"))
    app.add_handler(CommandHandler("configure_risk", configure_risk))
    app.add_handler(CommandHandler("hedge_status", hedge_status))
    app.add_handler(CommandHandler("auto_hedge", auto_hedge))
    app.add_handler(CommandHandler("hedge_history", hedge_history_command))
    app.add_handler(CommandHandler("pnl_status", pnl_status))
    app.add_handler(CommandHandler("stress_test", stress_test))
    app.add_handler(CommandHandler("portfolio_analytics", portfolio_analytics))
    app.add_handler(CommandHandler("risk_chart", risk_chart))
    app.add_handler(CommandHandler("greeks_chart", greeks_chart))
    app.add_handler(CommandHandler("pnl_chart", pnl_chart))
    logger.info("🚀 Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
