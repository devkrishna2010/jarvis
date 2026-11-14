"""
J.A.R.V.I.S. — Telegram Integration & Passcode 2681 Test Suite
Tests:
1. Authorized chat management and enrollment.
2. Passcode 2681 verification.
3. Multi-recipient state tracking.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from skills.telegram_backup import (
    load_authorized_chats,
    enroll_chat_id,
    PASSCODE,
    TELEGRAM_CHAT_ID
)


class TestTelegramPasscode(unittest.TestCase):
    def test_passcode_value(self):
        """Verifies passcode is exactly 2681 as requested."""
        self.assertEqual(PASSCODE, "2681")

    def test_owner_enrolled(self):
        """Verifies Dev is enrolled as owner by default."""
        data = load_authorized_chats()
        self.assertIn(str(TELEGRAM_CHAT_ID), data.get("chats", {}))

    def test_guest_enrollment_with_passcode(self):
        """Verifies a new user chat_id is cleanly enrolled."""
        test_guest_id = "123456789"
        is_new = enroll_chat_id(test_guest_id, {"first_name": "Tony", "username": "ironman"})
        data = load_authorized_chats()
        self.assertIn(test_guest_id, data.get("chats", {}))
        self.assertEqual(data["chats"][test_guest_id]["name"], "Tony")

        # Cleanup test entry
        if test_guest_id in data["chats"]:
            del data["chats"][test_guest_id]
            from skills.telegram_backup import save_authorized_chats
            save_authorized_chats(data)


if __name__ == "__main__":
    unittest.main()

