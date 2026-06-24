# Keymint PyQt Starter

A cross-platform desktop app using PyQt6 with Keymint license activation and machine binding.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
python main.py
```

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Description |
|---|---|
| `KEYMINT_CLIENT_API_KEY` | Client API key from [Keymint Dashboard](https://app.keymint.dev) |
| `KEYMINT_PRODUCT_ID` | Your product ID |

## What's Included

- **Activation dialog** — PyQt6 dialog prompting for a license key
- **Cross-platform machine ID** — Windows (WMIC), macOS (IOPlatformUUID), Linux (/etc/machine-id)
- **Persistent storage** — uses `QSettings` to store license state across sessions
- **Keymint Python SDK** — uses the official `keymint` package for API calls

## Project Structure

```
├── main.py               # App entry point, launches activation or main window
├── license_manager.py    # Keymint SDK calls, machine ID, license storage
├── activation_dialog.py  # PyQt6 activation dialog
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable template
```

## Dependencies

- `keymint` — Official Keymint Python SDK
- `PyQt6` — Cross-platform GUI framework
- `python-dotenv` — Environment variable loading
