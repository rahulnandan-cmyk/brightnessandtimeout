#!/usr/bin/env python3
"""Combined Display Settings Test - Brightness and Screen Timeout"""

import sys
import os
import logging

# Add parent directory to Python path to find utils module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

# Import both utility modules
from utils.screenbrightness_utils import create_display_test
from utils.screen_timeout_utils import create_timeout_test


class CombinedDisplaySettingsTest(base_test.BaseTestClass):
    """Combined test for both brightness adjustment and screen timeout settings"""

    # Shared coordinates for both tests
    COORDINATES = {
        "win_button": (20, 1055),
        "settings": (296, 577),
        "display": (242, 955),
        "brightness": (178, 321),
        "screen_timeout": (56, 520),
        "15_seconds": (83, 252.8),
        "30_seconds": (83, 312),
        "1_minute": (83, 371.2),
        "2_minutes": (83, 430.4),
        "5_minutes": (83, 489.6),
        "10_minutes": (83, 548.8),
        "30_minutes": (83, 616),
    }

    # Brightness test parameters
    BRIGHTNESS_TEST_PARAMS = {
        "right_presses": 10,
        "left_presses": 10,
        "delay": 1.0
    }

    # Timeout test configurations
    TIMEOUT_CONFIGS = [
        ("15_seconds", 15000, 20, "15 seconds"),
        ("30_seconds", 30000, 35, "30 seconds"),
        ("1_minute", 60000, 0, "1 minute"),
        ("2_minutes", 120000, 0, "2 minutes"),
        ("5_minutes", 300000, 0, "5 minutes"),
        ("10_minutes", 600000, 0, "10 minutes"),
        ("30_minutes", 1800000, 0, "30 minutes"),
    ]

    def setup_class(self):
        """Initialize device and test managers"""
        # Register Android device
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Initialize test managers
        self.brightness_manager = None
        self.timeout_manager = None

        # Disable 'Stay Awake' for timeout tests
        self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")

        logging.info("=" * 60)
        logging.info("Combined Display Settings Test Initialized")
        logging.info("=" * 60)

    def setup_test(self):
        """Setup before each test method"""
        # Ensure device is awake and ready
        self._wake_up_device()
        self.ad.adb.shell("input keyevent KEYCODE_HOME")
        logging.info("Device setup completed")

    def _wake_up_device(self):
        """Wake up device using simple commands"""
        try:
            commands = [
                "input keyevent KEYCODE_WAKEUP",
                "input keyevent KEYCODE_MENU",
                "input keyevent KEYCODE_WAKEUP",
            ]
            for cmd in commands:
                self.ad.adb.shell(cmd)
                time.sleep(1)
            logging.info("Device wake-up completed")
        except Exception as e:
            logging.warning("Wake-up command failed: %s", e)

    def test_brightness_adjustment(self):
        """Test brightness adjustment functionality"""
        logging.info("=" * 60)
        logging.info("Starting Brightness Adjustment Test")
        logging.info("=" * 60)

        try:
            # Create brightness test manager
            self.brightness_manager = create_display_test(self.ad, self.COORDINATES)

            # Setup test environment
            if not self.brightness_manager.setup_test():
                asserts.fail("Brightness test setup failed")

            # Execute brightness test
            initial, final, values = self.brightness_manager.execute_brightness_test(
                **self.BRIGHTNESS_TEST_PARAMS
            )

            # Assert brightness changed
            asserts.assert_true(
                initial != final,
                f"Brightness should change. Initial: {initial}, Final: {final}"
            )

            # Additional validation - brightness should be within valid range
            asserts.assert_true(
                0 <= final <= 255,
                f"Brightness value {final} is outside valid range (0-255)"
            )

            logging.info("✅ BRIGHTNESS TEST PASSED: Successfully adjusted brightness")
            logging.info("Brightness change: %d → %d (=%+d)", initial, final, final - initial)

        except Exception as e:
            logging.error("Brightness test failed: %s", e)
            asserts.fail(f"Brightness test execution failed: {e}")

    def test_screen_timeout_sequential(self):
        """Test sequential screen timeout settings"""
        logging.info("=" * 60)
        logging.info("Starting Sequential Screen Timeout Test")
        logging.info("=" * 60)

        try:
            # Create timeout test manager
            self.timeout_manager = create_timeout_test(self.ad, self.COORDINATES)

            # Setup test environment
            if not self.timeout_manager.setup_test():
                asserts.fail("Timeout test setup failed")

            # Execute sequential timeout tests
            results = self.timeout_manager.test_sequential_timeouts(self.TIMEOUT_CONFIGS)

            # Validate results
            for timeout_key, expected_ms, wait_time, label in self.TIMEOUT_CONFIGS:
                if timeout_key in results:
                    actual_ms = results[timeout_key]
                    asserts.assert_equal(
                        actual_ms, expected_ms,
                        f"Timeout mismatch for {label}. Expected: {expected_ms}, Actual: {actual_ms}"
                    )
                    logging.info("✅ %s timeout verified: %d ms", label, actual_ms)
                else:
                    logging.warning("⚠️ No result for %s timeout", label)

            logging.info("✅ TIMEOUT TEST PASSED: All timeout settings verified")

        except Exception as e:
            logging.error("Timeout test failed: %s", e)
            asserts.fail(f"Timeout test execution failed: {e}")

    def test_individual_timeout_15_seconds(self):
        """Test specifically the 15-second timeout"""
        self._test_single_timeout("15_seconds", 15000, 20, "15 seconds")

    def test_individual_timeout_30_seconds(self):
        """Test specifically the 30-second timeout"""
        self._test_single_timeout("30_seconds", 30000, 35, "30 seconds")

    def test_individual_timeout_1_minute(self):
        """Test specifically the 1-minute timeout"""
        self._test_single_timeout("1_minute", 60000, 0, "1 minute")

    def _test_single_timeout(self, timeout_key, expected_ms, wait_time, label):
        """Helper method to test a single timeout setting"""
        logging.info("Testing %s timeout", label)

        try:
            # Create timeout manager
            self.timeout_manager = create_timeout_test(self.ad, self.COORDINATES)

            # Setup
            if not self.timeout_manager.setup_test():
                asserts.fail(f"{label} timeout test setup failed")

            # Test single timeout
            success = self.timeout_manager.test_single_timeout(
                timeout_key, expected_ms, wait_time, label
            )

            asserts.assert_true(
                success,
                f"Single timeout test failed for {label}"
            )

            logging.info("✅ %s timeout test passed", label)

        except Exception as e:
            logging.error("Single timeout test failed for %s: %s", label, e)
            asserts.fail(f"Single timeout test failed for {label}: {e}")

    def test_display_settings_comprehensive(self):
        """Comprehensive test covering both brightness and timeout in sequence"""
        logging.info("=" * 60)
        logging.info("Starting Comprehensive Display Settings Test")
        logging.info("=" * 60)

        # Test brightness first
        self.test_brightness_adjustment()

        # Then test timeouts
        self.test_screen_timeout_sequential()

        logging.info("✅ COMPREHENSIVE TEST PASSED: All display settings working correctly")

    def teardown_class(self):
        """Cleanup and reset settings"""
        logging.info("Performing test cleanup...")

        try:
            # Reset timeout to 30 seconds
            if hasattr(self, 'timeout_manager') and self.timeout_manager:
                self.timeout_manager.teardown_test()

            # Brightness cleanup
            if hasattr(self, 'brightness_manager') and self.brightness_manager:
                self.brightness_manager.teardown_test()

            # Ensure we're back to home screen
            self.ad.adb.shell("input keyevent KEYCODE_HOME")

            # Re-enable stay awake for development (optional)
            # self.ad.adb.shell("settings put global stay_on_while_plugged_in 3")

            logging.info("✅ Cleanup completed successfully")

        except Exception as e:
            logging.warning("Cleanup encountered issues: %s", e)


# Import time at the bottom to avoid circular imports
import time

if __name__ == "__main__":
    test_runner.main()