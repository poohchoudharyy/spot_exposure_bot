# 📈 Spot Exposure Hedging Bot – GoQuant Backend Assignment

This project is a Telegram-integrated hedging system that manages directional risk in crypto spot positions. It calculates risk metrics and triggers hedging strategies using perpetual futures or options. The bot interacts with users via Telegram to monitor, manage, and report portfolio risks in real-time.

---

## 🔧 Features

- 🧠 **Risk Analytics**: Delta, Gamma, Theta, Vega, VaR, Max Drawdown
- 🔁 **Auto-Hedging Strategies**: Perpetual futures, Protective Puts, Covered Calls
- 📉 **Exchange Integration**: Binance, Bybit, OKX via `ccxt`
- 🤖 **Telegram Bot**: Interactive commands and inline buttons
- 📊 **Portfolio Analytics**: Real-time metrics and stress testing
- 💹 **PnL Tracking & History**: Logs all hedge activities and profit/loss

---

goquant-assignment/
├── main.py         ✅ Your full bot code
├── README.md       ✅ Just created
└── demo.mp4        ✅ (Optional - if you recorded screen walkthrough)

---

## 📂 System Architecture

```plaintext
[Exchange APIs (ccxt)]
       ⬇️
Price Fetch → Risk Calculator → Auto Hedge Logic
       ⬇️                   ⬇️
Telegram Bot Interface ← Hedge Execution & History Tracker
```

---

## 📜 Commands

| Command | Description |
|---------|-------------|
| `/start` | Launch the bot |
| `/monitor_risk <symbol> <position_size> <threshold> [exchange]` | Start monitoring an asset |
| `/configure_risk <threshold>` | Update risk threshold |
| `/auto_hedge <strategy> <threshold>` | Enable auto-hedging |
| `/hedge_status` | Show current status |
| `/hedge_now` | Execute hedge manually |
| `/hedge_history` | View hedge log |
| `/portfolio_analytics` | Show risk metrics |
| `/pnl_status` | View profit/loss summary |
| `/stress_test` | Run simulated stress tests |

---

## ⚙️ Setup Instructions

1. Clone the repo or extract files:
```bash
git clone <repo-url>
cd <folder name>
```

2. (Optional) Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Replace Telegram bot token inside `main()`:
```python
ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
```

5. Run the bot:
```bash
python main.py
```

---

## 📦 Requirements

- Python 3.8+
- `ccxt` for exchange API access
- `python-telegram-bot` for Telegram integration
- `asyncio`, `logging`, `datetime` (built-in)
- `matplotlib` for visualization and for charts

---

## 🧠 Risk Models

- **Delta**: `delta ≈ 0.8 * position_size`
- **VaR**: `VaR = Z * volatility * position_value`
- **Max Drawdown**: `8% of position`
- **Slippage**: `0.2% of price`

> These models are approximated for demonstration purposes.

---


## 🚀 Future Enhancements
- Real order execution with API keys
- Advanced auto-hedging logic
- Options-based hedging strategies
- Interactive charts and historical analytics
- Multi-user support with authentication



## 🎥 Video Demonstration : https://drive.google.com/file/d/1Q-YVBNtCVNx8TdJvlIbhrz2mwbVDqtNz/view?usp=drivesdk

Please refer to the attached video demonstrating:

- Setup using `/monitor_risk`
- Manual and auto hedging
- Analytics, stress testing, and PnL display

---

## ✍️ Author

- **Name:** Pooja Choudhary
- **Assignment:** GoQuant – Spot Hedging Bot



