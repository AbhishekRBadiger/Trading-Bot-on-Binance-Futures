# 🤖 Binance Futures Testnet Trading Bot

A clean, modular Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures REST API client (timestamp-synced)
│   ├── orders.py          # Order placement logic & response formatting
│   ├── validators.py      # CLI input validation (type, range, required combos)
│   └── logging_config.py  # Rotating file + console logging setup
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Template for API credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Steps

### 1. Get Binance Futures Testnet Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account (no KYC required)
3. Click your profile (top-right) → **"API Key"**
4. Click **Generate** — copy both the **API Key** and **Secret Key**
   > ⚠️ The Secret Key is shown **only once**. Save it immediately.
5. Go to **Assets** on the dashboard and claim free testnet USDT if your balance is 0

### 2. Clone / Download the Project

```bash
git clone <your-repo-url>
cd trading_bot
```

### 3. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_api_secret
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## 🚀 How to Run

### Syntax

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <ORDER_TYPE> --quantity <QTY> [--price <PRICE>] [--stop-price <STOP_PRICE>]
```

### Order Types Supported

| Type | Description | Required Args |
|------|-------------|---------------|
| `MARKET` | Executes immediately at current market price | `--quantity` |
| `LIMIT` | Executes at your specified price or better | `--quantity`, `--price` |
| `STOP_MARKET` | Triggers a market order when stop price is hit | `--quantity`, `--stop-price` |
| `STOP` | Triggers a limit order when stop price is hit | `--quantity`, `--price`, `--stop-price` |

### ⚠️ Minimum Order Size

Binance requires every order's notional value to be **at least 100 USDT**.

| Symbol | Min Quantity (approx) |
|--------|----------------------|
| BTCUSDT | `0.002` (~$168 at $84k BTC) |
| ETHUSDT | `0.05` (~$120 at $2400 ETH) |

If you get error `-4164`, increase your quantity.

---

## 💻 Run Examples

### ✅ Market BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### ✅ Limit SELL Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 100000
```

> Setting price above the current market keeps the order open (status: `NEW`) — this is expected for a limit order.

### ✅ Stop-Market BUY Order *(Bonus)*

```bash
python cli.py --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.05 --stop-price 2000
```

### ✅ Stop-Limit SELL Order *(Bonus)*

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.002 --stop-price 79000 --price 78500
```

---

## 📄 Sample Output

```
🚀 Binance Futures Testnet Trading Bot
=============================================

📋 Order Request Summary:
   Symbol     : BTCUSDT
   Side       : BUY
   Type       : MARKET
   Quantity   : 0.002

✅ Order Placed Successfully!
────────────────────────────────────────
   Order ID    : 3212345678
   Symbol      : BTCUSDT
   Status      : FILLED
   Side        : BUY
   Type        : MARKET
   Orig Qty    : 0.002
   Executed Qty: 0.002
   Avg Price   : 84231.50
────────────────────────────────────────
```

---

## ❌ Validation & Error Handling

The bot validates all inputs before sending anything to the API.

| Scenario | Error Message |
|----------|--------------|
| Missing required argument | `argparse` prints usage and exits |
| Invalid side (e.g. `LONG`) | `invalid choice: LONG (choose from BUY, SELL)` |
| LIMIT order without `--price` | `❌ Validation Error: Price is required for LIMIT orders.` |
| Negative quantity | `❌ Validation Error: Quantity must be greater than 0.` |
| Order below $100 notional | `❌ API Error: Order's notional must be no smaller than 100` |
| No `.env` / missing credentials | Clear setup instructions printed, exits cleanly |
| Network failure | `❌ Network Error: Could not reach Binance Testnet.` |
| Clock skew | Handled automatically — bot syncs timestamp with Binance server |

---

## 📋 Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

- Rotates at **5 MB**, keeping up to **3 backups**
- `DEBUG` level written to file, `WARNING` and above shown in terminal
- Format: `timestamp | level | module | message`

**Sample log entries:**
```
2026-03-14 11:55:41 | INFO     | bot.client | REQUEST POST https://testnet.binancefuture.com/fapi/v1/order | params: {...}
2026-03-14 11:55:41 | INFO     | bot.client | RESPONSE 200 | {"orderId": 3212345678, "status": "FILLED", ...}
```

---

## 📦 Dependencies

```
requests>=2.31.0       # HTTP calls to Binance REST API
python-dotenv>=1.0.0   # Load .env credentials
```

No third-party Binance SDK used — all API calls are direct REST requests.

---

## 🔒 Assumptions

- **Testnet only** — hardcoded to `https://testnet.binancefuture.com`. Do not use with real mainnet credentials.
- **USDT-M Futures** — all orders placed on USDT-Margined perpetual contracts.
- **Timestamp sync** — the bot fetches server time from Binance before each signed request to avoid clock skew errors (`-1021`).
- **Quantity precision** — enter quantities that respect the symbol's step size. The API will return a clear error if precision is off.
- **Leverage** — uses whatever leverage is set on your testnet account (default: 20x). The bot does not change leverage.
- **Testnet funds** — claim free USDT from the testnet dashboard if needed.
