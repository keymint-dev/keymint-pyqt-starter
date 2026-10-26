"""Tests offline_license.py with a throwaway Ed25519 key, signing .lic files
the way the Keymint server does. Run: python -m unittest discover tests"""
import base64
import hashlib
import json
import os
import sys
import time
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from offline_license import check_offline_license  # noqa: E402

KEY = Ed25519PrivateKey.generate()
PEM = KEY.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
DER = KEY.public_key().public_bytes(
    serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
NOW = int(time.time())


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def lic(**claims) -> str:
    kid = b64(hashlib.sha256(DER).digest())
    payload = {"productId": "prod_1", "machineCode": "machine-1", "type": "offline",
               "iat": NOW, "exp": NOW + 86400, "sub": "KM-TEST", **claims}
    signing_input = f"{b64(json.dumps({'alg': 'EdDSA', 'kid': kid}).encode())}.{b64(json.dumps(payload).encode())}"
    token = f"{signing_input}.{b64(KEY.sign(signing_input.encode()))}"
    return json.dumps({"signedDate": "2026-10-26T00:00:00.000Z", "signedKey": token, "keyId": kid})


def check(contents, machine="machine-1", last_trusted=0.0, public_key=PEM):
    return check_offline_license(contents, public_key=public_key, product_id="prod_1",
                                 machine_code=machine, last_trusted=last_trusted)


class OfflineLicenseTest(unittest.TestCase):
    def test_valid_file(self):
        result = check(lic())
        self.assertTrue(result["success"])
        self.assertEqual(result["license"].license_key, "KM-TEST")
        self.assertEqual(result["license"].expires_at.timestamp(), NOW + 86400)
        self.assertGreaterEqual(result["trusted_at"], NOW)

    def test_clock_rollback_uses_last_trusted(self):
        result = check(lic(), last_trusted=NOW + 2 * 86400)
        self.assertFalse(result["success"])
        self.assertIn("expired", result["message"])

    def test_messages_per_code(self):
        self.assertIn("newly signed", check(lic(exp=NOW - 3600))["message"])
        self.assertIn("different machine", check(lic(), machine="machine-2")["message"])
        self.assertIn("different product", check(lic(productId="prod_2"))["message"])

    def test_invalid_files(self):
        tampered = lic().replace('"signedKey": "', '"signedKey": "x')
        for contents in (tampered, "not a license", "{}", "x" * 70000):
            self.assertIn("not a valid offline license", check(contents)["message"])

    def test_configuration_errors(self):
        self.assertIn("not configured", check(lic(), public_key="")["message"])
        self.assertIn("misconfigured", check(lic(), public_key="nope")["message"])


if __name__ == "__main__":
    unittest.main()
