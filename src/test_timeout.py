#!/usr/bin/env python3
# src/test_timeout.py
"""Screen Timeout Sequential Test using Common Utils"""
import logging
from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

from utils.common_utils import create_display_test


class ScreenTimeoutTest(base_test.BaseTestClass):
    """Sequentially validate screen timeout settings from 15s to 30min."""

    def setup_class(self):
        """Initialize device and test manager."""
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Coordinates for timeout test
        self.coords = {
            "win_button": (20, 1055),
            "settings": (296, 577),
            "display": (242, 955),
            "screen_timeout": (56, 520),
            "15_seconds": (83, 252.8),
            "30_seconds": (83, 312),
            "1_minute": (83, 371.2),
            "2_minutes": (83, 430.4),
            "5_minutes": (83, 489.6),
            "10_minutes": (83, 548.8),
            "30_minutes": (83, 616),
        }

        # Create test manager
        self.test_manager = create_display_test(self.ad, self.coords)

        # Disable stay awake
        logging.info("Disabling developer 'Stay Awake' option...")
        self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")

    def test_sequential_timeouts(self):
        """Run sequential timeout tests from 15s → 30min."""
        logging.info("=" * 60)
        logging.info("Starting Screen Timeout Sequential Test")
        logging.info("=" * 60)

        timeout_list = [
            ("15_seconds", 15000, 20),
            ("30_seconds", 30000, 35),
            ("1_minute", 60000, 65),  # Increased wait time
            ("2_minutes", 120000, 0),
            ("5_minutes", 300000, 0),
            ("10_minutes", 600000, 0),
            ("30_minutes", 1800000, 0),
        ]

        # Setup once for all tests
        if not self.test_manager.setup_test():
            asserts.fail("Test setup failed")

        try:
            for key, expected_ms, wait_sec in timeout_list:
                success = self.test_manager.execute_timeout_test(key, expected_ms, wait_sec)
                asserts.assert_true(success, f"Timeout test failed for {key}")

            logging.info("✓ All timeout tests completed successfully")

        except Exception as e:
            logging.error("Test sequence failed: %s", e)
            asserts.fail(f"Test sequence failed: {e}")

    def teardown_class(self):
        """Reset screen timeout to 30 seconds and cleanup."""
        logging.info("Resetting screen timeout to 30 seconds...")

        try:
            # Setup for teardown
            self.test_manager.setup_test()

            # Set to 30 seconds
            self.test_manager.execute_timeout_test("30_seconds", 30000, 0)

            # Teardown (goes to home)
            self.test_manager.teardown_test()

        except Exception as e:
            logging.warning("Teardown had issues: %s", e)

        logging.info("Test completed.")


if __name__ == "__main__":
    test_runner.main()
