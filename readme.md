# TradeBot

TradeBot is an automated trading system that uses various strategies to optimize portfolio performance. It integrates with Alpaca for live trading and Yahoo Finance for backtesting.

## Features

- **Momentum Trading:** Executes trades based on momentum indicators.
- **Random Trading:** Simulates random buy/sell actions for testing.
- **Transaction Filtering:** Filters trades based on spread limits.
- **AI Plan Revision:** Uses AI to revise trading plans.
- **Backtesting:** Test strategies using historical data.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/tradebot.git
   cd tradebot
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**

   Create a `.env` file in the root directory with your Alpaca and Azure OpenAI credentials:

   ```plaintext
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_API_SECRET=your_alpaca_api_secret
   ALPACA_PAPER=True
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_DEPLOYMENT_NAME=your_azure_deployment_name
   ```

## Usage

- **Run the Application:**

  ```bash
  python src/main.py
  ```

- **Backtesting:**

  Use the UI to set start and end dates for backtesting. Logs and settings will be saved in the `logs` directory.

## Testing

- **Run Unit Tests:**

  ```bash
  pytest tests/
  ```

## Linting

- **Run Linter:**

  ```bash
  pylint src
  ```

## Important Directories

- **`src/`:** Contains the main application code, including `main.py`, `logger_setup.py`, and the `logic_modules` package.
- **`tests/`:** Contains unit tests for the application.
- **`logs/`:** Stores log files generated during application execution.

## Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.