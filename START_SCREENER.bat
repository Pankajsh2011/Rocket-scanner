@echo off
echo ============================================================
echo   INDIA STOCK SCREENER PRO - NSE/BSE
echo   50 Screeners + Institutional + News + AI Signals
echo ============================================================
echo.
echo Starting server on http://localhost:5050
echo.
echo [Features]
echo   - 50 Screener Modes (Momentum, Breakout, Reversal etc.)
echo   - Entry / Stop Loss / Target / Exit signals
echo   - Institutional Holdings Tracker
echo   - Live NSE/BSE Market Data
echo   - India + Global Market News (MC, ET, BS, Reuters)
echo   - AI Market Sentiment Analysis
echo   - Nifty50 / Nifty100 / All Stocks scan
echo.
echo Press Ctrl+C to stop the server.
echo.
cd /d %~dp0
python app.py
pause
