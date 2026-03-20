# telegram-finance-agent

Telegram-based finance tracker with a lightweight web UI for reviewing income and expense messages.

## What this project is
This repository is an experimental personal-finance utility built around Telegram message flows.
It combines a Telegram parser, data extraction scripts, and a small browser interface for viewing transactions.

## What it does
- Connects to Telegram using user API credentials
- Reads messages from selected groups/chats
- Separates income and expense streams
- Stores parsed transactions locally
- Exposes a lightweight web interface for browsing the data

## Repository structure
- `app.py` / `telegram_server.py` — local web app entry points
- `telegram_parser.py` / `run_parser.py` — Telegram parsing flow
- `ParserQ/` — parser utilities and data extraction helpers
- `templates/` — web UI templates
- `config.json` — local config template (do not commit real secrets)

## Setup
1. Create your Telegram API credentials at `https://my.telegram.org`
2. Put your real values into a local config file
3. Keep all secrets and session files out of git

Example config shape:

```json
{
  "api_id": 123456,
  "api_hash": "your_api_hash",
  "phone_number": "+1234567890",
  "group_ids": [-1001234567890, -1000987654321]
}
```

## Run
```bash
pip install -r requirements.txt
python app.py
```

## Notes
- This is a practical utility project, not a polished SaaS product
- Session files, API keys, and local caches should never be committed
- A future cleanup could split parser, backend, and UI into clearer modules
