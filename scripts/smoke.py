"""Smoke test: exercises the keymint Python SDK surface used by this starter
end to end against the test workspace, then cleans up.

Required env: KEYMINT_TEST_ADMIN_API_KEY, KEYMINT_TEST_CLIENT_API_KEY,
KEYMINT_TEST_PRODUCT_ID. Skips quietly when absent (PR runs).
"""
import os
import sys
import uuid

ADMIN_KEY = os.environ.get("KEYMINT_TEST_ADMIN_API_KEY")
CLIENT_KEY = os.environ.get("KEYMINT_TEST_CLIENT_API_KEY")
PRODUCT_ID = os.environ.get("KEYMINT_TEST_PRODUCT_ID")
BASE_URL = os.environ.get("KEYMINT_TEST_BASE_URL", "https://api.keymint.dev")

if not ADMIN_KEY or not CLIENT_KEY or not PRODUCT_ID:
    print("smoke: credentials not set, skipping")
    sys.exit(0)

from keymint import KeyMint  # noqa: E402

admin = KeyMint(api_key=ADMIN_KEY, base_url=BASE_URL)
client = KeyMint(api_key=CLIENT_KEY, base_url=BASE_URL)
run_id = uuid.uuid4().hex
host_id = f"smoke-pyqt-{run_id}"
license_key = None
failed = False


def check(label, cond, extra=""):
    global failed
    print(f"{'PASS' if cond else 'FAIL'} {label} {extra}")
    if not cond:
        failed = True


try:
    created = admin.create_key({
        "productId": PRODUCT_ID,
        "maxActivations": "2",
        "metadata": {"purpose": "pyqt-starter-smoke", "runId": run_id},
    })
    license_key = created.get("key")
    check("create", bool(license_key))

    lookup = admin.get_key({"productId": PRODUCT_ID, "licenseKey": license_key})
    check("get", (lookup.get("data") or {}).get("license", {}).get("productId") == PRODUCT_ID)

    activation = client.activate_key({
        "productId": PRODUCT_ID, "licenseKey": license_key, "hostId": host_id,
    })
    check("activate", activation.get("code") == 0, str(activation.get("message")))

    deactivated = client.deactivate_key({
        "productId": PRODUCT_ID, "licenseKey": license_key, "hostId": host_id,
    })
    check("deactivate", deactivated.get("devicesRemoved") == 1, str(deactivated))

    admin.block_key({"productId": PRODUCT_ID, "licenseKey": license_key})
    print("PASS block")
    admin.unblock_key({"productId": PRODUCT_ID, "licenseKey": license_key})
    print("PASS unblock")
except Exception as e:  # noqa: BLE001
    print(f"FAIL exception: {e}")
    failed = True
finally:
    if license_key:
        try:
            admin.block_key({"productId": PRODUCT_ID, "licenseKey": license_key})
            print("PASS cleanup-block")
        except Exception as e:  # noqa: BLE001
            print(f"FAIL cleanup-block: {e}")
            failed = True

sys.exit(1 if failed else 0)
