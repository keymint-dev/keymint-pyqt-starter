import hashlib
import platform
import subprocess
import uuid
import os
from PyQt6.QtCore import QSettings
from keymint import KeyMint

PRODUCT_ID = os.environ.get("KEYMINT_PRODUCT_ID", "")
CLIENT_API_KEY = os.environ.get("KEYMINT_CLIENT_API_KEY", "")
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


def deactivate_license() -> bool:
    license_key = get_stored_key()
    if not license_key:
        return False
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
