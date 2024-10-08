# exchange-changelog-helper

## Installation

### Install Singlefile CLI

Follow the [Singlefile CLI Installation Guide](https://github.com/gildas-lormeau/single-file-cli?tab=readme-ov-file#installation).

### Install Poetry

To install Poetry, first install `pipx` and then use `pipx` to install Poetry:

```sh
pip install pipx
pipx install poetry
```

### Install Python Dependencies

Install the required Python dependencies using Poetry:

```sh
poetry install
```

### API Key Configuration

Create a `.env` file in the root directory of your project and add your API keys:

```env
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the main script using Poetry:

```sh
poetry run python main.py
```

Result (2024-09-25~2024-10-09):

```
# binance

https://developers.binance.com/docs/derivatives/change-log

CHANGELOG:
- 2024-10-08: COIN-M Futures: The most recent 7-days data is returned by default when requesting the following endpoints. The query time period for these endpoints must be less than 7 days: GET /dapi/v1/allOrders GET /dapi/v1/userTrades. The following endpoints will be adjusted to keep only recent three month data: GET /dapi/v1/order GET /dapi/v1/allOrders.
- 2024-09-27: USDⓈ-M Futures: The following websocket user data requests are deprecated: listenkey@account listenkey@balance listenkey@position. COIN-M Futures: The following websocket user data requests are deprecated: listenkey@account listenkey@balance listenkey@position.




# bybit

https://bybit-exchange.github.io/docs/changelog/v5

CHANGELOG:
- 2024-09-29: Websocket API Order [UPDATE] Add new response field closedPnl Execution [UPDATE] Add a response field execPnl




# okx

https://www.okx.com/docs-v5/log_en/#upcoming-changes

CHANGELOG:
- 2024-10-04: Added call auction details WebSocket channel WS / Call auction details channel.
- 2024-10-01: Added public feature for endpoint: GET / Announcements.

```
