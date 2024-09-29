# TradeBot

TradeBot is an algorithmic trading bot using Alpaca API and Lumibot for backtesting and live trading. It uses sentiment analysis based on news to make decisions on a variety of assets.

## Features
- Portfolio optimization using `PyPortfolioOpt`
- Sentiment analysis using `finbert_utils`
- Historical data fetching via the Alpaca API

## Requirements
- Python 3.8+
- Alpaca API account
- Lumibot
- PyTorch
- PyPortfolioOpt

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
Activate the virtual environment:

bash
Copy code
# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Create a .env file with your Alpaca API credentials:

bash
Copy code
ALPACA_API_KEY=your_api_key
ALPACA_API_SECRET=your_api_secret
ALPACA_PAPER=True
ALPACA_BASE_URL=https://paper-api.alpaca.markets
Usage
Run the backtest:
bash
Copy code
python tradebot.py