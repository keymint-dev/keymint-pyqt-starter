import hashlib
import platform
import subprocess
import uuid
import os
from PyQt6.QtCore import QSettings
from keymint import KeyMint
from dotenv import load_dotenv
from offline_license import check_offline_license

# Load .env before reading settings. main.py imports this module before its
# own load_dotenv() call runs, so reading here first would miss .env values.
load_dotenv()

PRODUCT_ID = os.environ.get("KEYMINT_PRODUCT_ID", "")
CLIENT_API_KEY = os.environ.get("KEYMINT_CLIENT_API_KEY", "")
# Optional, for offline licenses: PEM from Developer -> Public Keys. In .env,
# use a quoted multi-line value or write the line breaks as \n.
PUBLIC_KEY = os.environ.get("KEYMINT_PUBLIC_KEY", "").replace("\\n", "\n").strip()
client = KeyMint(api_key=CLIENT_API_KEY)
settings = QSettings("KeymintStarter", "PyQtLicenseStarter")


def get_host_id() -> str:
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output(
                "wmic csproduct get uuid", shell=True
            )
            raw = output.decode().split("\n")[1].strip()
        elif system == "Darwin":
            output = subprocess.check_output(
                "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID",
                shell=True,
            )
            raw = output.decode().split('"')[-2]
        else:
            with open("/etc/machine-id") as f:
                raw = f.read().strip()
    except Exception:
        raw = str(uuid.getnode())

    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_stored_key() -> str | None:
    val = settings.value("license/key")
    return val if val else None


def is_activated() -> bool:
    return settings.value("license/activated", False, type=bool)


def activate_license(license_key: str) -> dict:
    host_id = get_host_id()
    try:
        result = client.activate_key({
            "productId": PRODUCT_ID,
            "licenseKey": license_key,
            "hostId": host_id,
        })
        if result.get("code") == 0:
            settings.setValue("license/key", license_key)
            settings.setValue("license/activated", True)
            return {"success": True, "message": result.get("message", "License valid")}
        return {"success": False, "message": result.get("message", "Activation failed")}
    except Exception as e:
        return {"success": False, "message": str(e)}


def _check_offline(contents: str) -> dict:
    result = check_offline_license(
        contents, public_key=PUBLIC_KEY, product_id=PRODUCT_ID, machine_code=get_host_id(),
        last_trusted=settings.value("license/last_trusted", 0.0, type=float),
    )
    if result["success"]:
        settings.setValue("license/last_trusted", result["trusted_at"])
    return result


def import_offline_license(path: str) -> dict:
    """Verifies a .lic file and, if valid, stores it."""
    try:
        with open(path, encoding="utf-8") as f:
            contents = f.read(64 * 1024 + 1)
    except (OSError, UnicodeDecodeError):
        return {"success": False, "message": "Could not read the license file."}
    result = _check_offline(contents)
    if result["success"]:
        settings.setValue("license/offline_file", contents)
    return result


def check_stored_offline_license() -> dict | None:
    """Re-verifies the stored .lic file; None if there isn't one."""
    contents = settings.value("license/offline_file")
    return _check_offline(contents) if contents else None


def deactivate_license() -> bool:
    license_key = get_stored_key()
    if not license_key:
        # Offline licenses aren't tracked by the server; just forget the file.
        # license/last_trusted stays, so an old file can't use a rolled-back clock.
        if not settings.value("license/offline_file"):
            return False
        settings.remove("license/offline_file")
        return True
    host_id = get_host_id()
    try:
        result = client.deactivate_key({
            "productId": PRODUCT_ID,
            "licenseKey": license_key,
            "hostId": host_id,
        })
        if result.get("code") == 0:
            settings.remove("license/key")
            settings.remove("license/activated")
            return True
        return False
    except Exception:
        return False
