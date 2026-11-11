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
| `KEYMINT_CLIENT_API_KEY` | API key with the `client` scope from the [Keymint Dashboard](https://app.keymint.dev) (starts with `km_live_`). Never ship an admin key in the app. |
| `KEYMINT_PRODUCT_ID` | Your product ID |
| `KEYMINT_PUBLIC_KEY` | Optional. Public key PEM for [offline licenses](#offline-licenses) |

## What's Included

- **Activation dialog** — PyQt6 dialog prompting for a license key
- **Stable installation ID** — the `hostId` comes from the SDK's `identity.get_or_create_installation_id()`: a 64-character SHA-256 ID saved in `~/.keymint/installation-id` and reused on every launch. If it can't be read or saved, the app shows an error instead of using a shared or temporary ID.
- **Persistent storage** — uses `QSettings` to store license state across sessions
- **Keymint Python SDK** — uses the official `keymint` package for API calls

## Offline Licenses

For machines without internet access, the user can import a `.lic` file instead of entering a key ("Import offline license" in the activation dialog). The app verifies it locally with the SDK's `verify_offline_license`.

1. **Public key**: copy the PEM from **Developer → Public Keys** in the dashboard into `KEYMINT_PUBLIC_KEY` (quoted multi-line value, or line breaks written as `\n`). It's a public key, safe to ship.
2. **The `.lic` file**: create it in the dashboard (a license's activations → **Create offline license**) or from your backend with the SDK's `sign_key` (admin API key; never call it from the app). Sign it for the machine ID from `get_host_id()`, the same `hostId` used for online activation.
3. The file must match `KEYMINT_PRODUCT_ID` and this machine. When it expires, the user imports a newly signed file.

The file is stored in `QSettings` and re-checked on launch. Expiry is checked against the later of the system clock and the last time a check succeeded, so setting the clock back doesn't extend it. Online activation works as before; offline is an extra path.

Tests: `python -m unittest discover tests`.

## Upgrading from an earlier version of this starter

Earlier versions used a 16-character hash of the hardware ID as the `hostId`. This version uses the SDK's installation ID instead, so an existing install reports a new `hostId`: on next launch it activates as a new device (using another activation slot, or failing with `activation_limit_reached` if none is left; remove the old device from the license in the dashboard), and offline `.lic` files signed for the old ID must be signed again for the new one.

## Project Structure

```
├── main.py               # App entry point, launches activation or main window
├── license_manager.py    # Keymint SDK calls, installation ID, license storage
├── offline_license.py    # Offline .lic verification
├── activation_dialog.py  # PyQt6 activation dialog
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variable template
```

## Dependencies

- `keymint` — Official Keymint Python SDK
- `PyQt6` — Cross-platform GUI framework
- `python-dotenv` — Environment variable loading
