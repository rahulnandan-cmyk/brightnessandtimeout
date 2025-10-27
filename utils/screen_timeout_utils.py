#!/usr/bin/env python3
# test_timeout.py
"""Sequential Screen Timeout Test using Mobly + UIAutomator2."""

import logging
import time
from mobly import base_test, test_runner
from mobly.controllers import android_device
from utils.screen_timeout_utils import TimeoutTestManager  # ← import your utility


class ScreenTimeoutTest(base_test.BaseTestClass):
    """Mobly test that validates screen timeout options using TimeoutTestManager."""

    def setup_class(self):
        """Register device and create TimeoutTestManager instance."""
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Create the utility manager
        self.manager = TimeoutTestManager(self.ad)

        # Configure logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info("===== Screen Timeout Test Setup =====")
        assert self.manager.setup_test(), "Device setup failed!"

    def test_sequential_screen_timeouts(self):
        """Run sequential screen timeout validation using TimeoutTestManager."""
        logging.info("===== Starting Sequential Timeout Test =====")

        # Each tuple: (timeout_text, expected_ms, wait_sec)
        timeout_configs = [
            ("15 seconds", 15000, 20),
            ("30 seconds", 30000, 35),
            ("1 minute", 60000, 65),
            ("2 minutes", 120000, 125),
            ("5 minutes", 300000, 0),
            ("10 minutes", 600000, 0),
            ("30 minutes", 1800000, 0),
        ]

        # Run through the utility manager
        self.manager.test_sequential_timeouts(timeout_configs)

    def teardown_class(self):
        """Reset to 30s timeout using the manager’s teardown."""
        logging.info("===== Starting Teardown =====")
        self.manager.teardown_test(default_timeout_ms=30000)
        logging.info("===== Teardown Completed =====")


# ---------------- Main Runner ----------------
if __name__ == "__main__":
    test_runner.main()
