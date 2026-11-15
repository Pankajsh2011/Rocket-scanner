# 🚀 RocketScan: 20%+ Circuit Stock Screener & Paper Trading

> **NSE & BSE Real-Time Technical Screener, 20%+ Single-Day Circuit Rocket Scanner, 80%-120% Quantitative Confluence Engine & Live Paper Trading Platform.**

---

## 🌟 Key Features

1. **🚀 20%+ Single-Day Circuit Rockets**:
   - Strictly scans and filters Indian equities with **Day Percentage (`ret_1d`) ≥ 20.0%**.
   - Identifies explosive momentum and upper circuit locks across 4,200+ NSE and BSE stocks.

2. **🎯 80% to 120% Quantitative Confluence Rating**:
   - Multi-factor mathematical scoring:
     - **80% - 89%**: Standard Solid Technical Setup
     - **90% - 99%**: High Conviction Institutional Confluence
     - **100% - 109%**: Perfect Multi-Indicator Confluence
     - **110% - 120%**: Alpha Over-Performer (20%+ Circuit Rockets & 3x+ Volume Surges)

3. **📝 Risk-Free Virtual Paper Trading**:
   - Pre-loaded with **₹10,00,000 (10 Lakhs Virtual Capital)**.
   - 1-Click execution on Signal Cards, Rocket Cards, and Detail Modal.
   - Real-time Unrealized P&L calculation, Target / Stop-Loss tracking, and 1-click position square-off.

4. **⚡ Ultra-Fast Multi-Threaded Parallel Scanning**:
   - Powered by `concurrent.futures.ThreadPoolExecutor(max_workers=12)`.
   - Scans 50 stocks in under 3 to 4 seconds.
   - Full **Instant Stop Control (`⏹️ STOP SCAN`)** to abort anytime.

5. **🕒 Live Indian Market Timing Engine**:
   - Automatically tracks IST (UTC+5:30) trading sessions:
     - `🟢 LIVE MARKET OPEN` (09:15 - 15:30 IST)
     - `🟡 PRE-MARKET SESSION` (09:00 - 09:15 IST)
     - `🟠 POST-MARKET` (15:30 - 16:00 IST)
     - `🔴 MARKET CLOSED` (Weekends & Holidays)
   - Built-in **Live Auto-Refresh (30s)** toggle.

6. **📊 5-Segment LED Trend Meter (0-100%)**:
   - Combines EMA 20/50/200, SuperTrend, ADX, RSI, and MACD into a visual 5-segment LED gauge.

---

## 🚀 Quick Local Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python app.py
```
Open your browser at: **`http://localhost:5050`**

---

## ☁️ How to Deploy on GitHub & Render (Free)

### Step 1: Push Code to GitHub

1. Open **[GitHub.com](https://github.com/)** and click **New Repository**.
2. Name your repository (e.g., `rocketscan-screener`). Set it to **Public** or **Private**, and leave "Add a README" **unchecked**.
3. In your local terminal, run:

```bash
cd C:\Users\Dell\india-screener
git add .
git commit -m "Initial commit: RocketScan 20%+ Screener, 80-120% Accuracy & Paper Trading"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/rocketscan-screener.git
git push -u origin main
```

---

### Step 2: Deploy on Render (Free 750 Hrs/Mo)

1. Go to **[Render.com](https://render.com/)** and sign in with your GitHub account.
2. Click **New +** → **Web Service**.
3. Select your repository (`rocketscan-screener`).
4. Configure the settings:
   - **Name**: `rocketscan`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: `Free`
5. Click **Create Web Service**.
6. Render will build and deploy your app in ~2 minutes! Your live public URL will be:
   **`https://rocketscan.onrender.com`**

---

## 📱 Mobile App (Android APK)

The repository includes a ready-to-build Android Capacitor/Cordova app in `mobile-app/`.
Run `python sync_mobile.py` to keep web assets synchronized.
