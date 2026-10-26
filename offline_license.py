"""Offline .lic verification. No Qt here, so it can be unit-tested."""
from datetime import datetime, timezone
from keymint import OfflineLicenseError, verify_offline_license

MAX_FILE_CHARS = 64 * 1024

MESSAGES = {
    "expired": "This offline license has expired. Get a newly signed .lic file from the vendor while online.",
    "wrong_machine": "This offline license was issued for a different machine.",
    "wrong_product": "This offline license is for a different product.",
}
INVALID = "This is not a valid offline license file for this app."


def check_offline_license(contents: str, *, public_key: str, product_id: str,
                          machine_code: str, last_trusted: float = 0.0) -> dict:
    """Verifies a .lic file for this product and machine.

    Expiry is checked against max(system time, last_trusted) so setting the
    clock back doesn't revive an expired file. On success, ``trusted_at`` is
    the new last-trusted time to store.
    """
    if not public_key or not product_id:
        return {"success": False, "message": "Offline licenses are not configured: "
                "set KEYMINT_PUBLIC_KEY and KEYMINT_PRODUCT_ID in .env"}
    if len(contents) > MAX_FILE_CHARS:
        return {"success": False, "message": INVALID}

    now = max(datetime.now(timezone.utc), datetime.fromtimestamp(last_trusted, timezone.utc))
    try:
        offline = verify_offline_license(contents, public_keys=[public_key], product_id=product_id,
                                         machine_code=machine_code, now=now)
    except OfflineLicenseError as e:
        return {"success": False, "message": MESSAGES.get(e.code, INVALID)}
    except (ValueError, TypeError) as e:
        # Bad options, e.g. KEYMINT_PUBLIC_KEY isn't an Ed25519 public key PEM.
        return {"success": False, "message": f"Offline licenses are misconfigured: {e}"}
    return {"success": True, "license": offline, "trusted_at": now.timestamp()}
