# Telegram Finance Agent

Telegram-based finance tracker with a lightweight web UI for reviewing income and expense messages.

This project explores how chat-based finance notes can be converted into structured records, dashboards, and reports.

## Problem

In many small businesses, financial activity is written in Telegram chats as short messages:

- incoming payments
- expenses
- purchases
- delivery costs
- cash movements
- comments from different people

This is convenient for quick communication, but difficult for later analysis.

## Solution

`telegram-finance-agent` connects to selected Telegram chats, reads messages, extracts finance-like entries, and exposes them through a lightweight browser interface.

## What it does

- Connects to Telegram using user API credentials
- Reads messages from selected groups/chats
- Separates income and expense streams
- Stores parsed transactions locally
- Exposes a lightweight web interface for browsing the data
- Creates a foundation for future reporting and reconciliation

## Architecture

```text
Telegram group messages
   ↓
Telegram parser
   ↓
Data extraction logic
   ↓
Local transaction store
   ↓
Web interface
   ↓
Finance review / reports
```

## Repository structure

- `app.py` / `telegram_server.py` — local web app entry points
- `telegram_parser.py` / `run_parser.py` — Telegram parsing flow
- `ParserQ/` — parser utilities and data extraction helpers
- `templates/` — web UI templates
- `config.json` — local config template, do not commit real secrets

## Setup

1. Create Telegram API credentials at `https://my.telegram.org`.
2. Put real values into a local config file.
3. Keep all secrets and session files out of git.

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

## Security notes

- Do not commit Telegram API secrets
- Do not commit Telegram session files
- Do not publish real private financial data
- Use anonymized messages for screenshots or demo data

## Why this project matters

This project demonstrates a practical automation pattern:

1. Take messy operational data from chat.
2. Parse it into structure.
3. Store it.
4. Display it in a simple interface.
5. Prepare it for reporting and decision-making.

That pattern is useful far beyond finance: orders, support tickets, delivery logs, production updates, and CRM workflows can follow a similar approach.

## Next improvements

- [ ] Add anonymized sample Telegram messages
- [ ] Add parser test cases
- [ ] Add CSV export
- [ ] Add date filters
- [ ] Add monthly summary view
- [ ] Add category detection
- [ ] Add screenshots of the web UI
- [ ] Add setup troubleshooting notes

## Target portfolio roles

This project supports positioning for:

- AI Automation Engineer
- Internal Tools Developer
- Business Automation Consultant
- Technical Product Engineer
- Data extraction / workflow automation developer
