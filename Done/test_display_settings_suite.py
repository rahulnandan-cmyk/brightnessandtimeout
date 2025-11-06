#!/usr/bin/env python3
"""Test Suite for Display Settings (Brightness and timeout)."""

import logging
import os
import sys
from typing import Dict, Any, List, Tuple, Optional

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

from utils.display_settings_manager import create_display_settings_manager, DisplaySettingsManager

# Add the parent directory to Python path to find 'utils' module
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
class DisplaySettings(base_test.BaseTestClass):
    """Test suite to validate display settings,
    including brightness adjustments and screen timeouts."""

    # Configurations
    BRIGHTNESS_TEST_PARAMS: Dict[str, Any] = {
        "right_press": 10,
        "left_press": 10,
        "delay": 1.0
    }

    TIMEOUT_CONFIGS: List[Tuple[str, int, int]] = [
        ("15 seconds", 15000, 20),
        ("30 seconds", 30000, 35),
        ("1 minute", 60000, 0),
        ("2 minutes", 120000, 0),
        ("5 minutes", 300000, 0),
        ("10 minutes", 600000, 0),
        ("30 minutes", 1800000, 0),
    ]

    test_manager: Optional[DisplaySettingsManager] = None
    ads: Optional[list] = None
    ad: Optional[android_device.AndroidDevice] = None

    def setup_class(self):
        """Get the device and initialize the manager."""
        logging.info("---setup class: Initializing Device and Manager---")

        # 1. Register and get the Android device
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # 2. Create the unified test manager instance using factory function
        self.test_manager = create_display_settings_manager(self.ad)


    def teardown_class(self):
        """Cleanup via test manager: Resetting timeout and general cleanup."""
        logging.info("---teardown_class: Running Teardown---")
        if self.test_manager:
            self.test_manager.teardown_test()


    def setup_test(self):
        """Per-test setup: Ensure the device is ready."""
        logging.info("---setup_test: Running Setup---")

        # Call the managers' setup routine
        if not self.test_manager.setup_test():
            asserts.fail("Test manager setup failed")


    # 1. Brightness adjustment
    def test_brightness(self):
        """Verifies that the brightness can be adjusted up and down
            and returns to original level."""

        logging.info("=" * 60)
        logging.info("Starting Brightness Adjustment Cycle test")
        logging.info("=" * 60)

        try:
            # Execute brightness test
            initial, final = self.test_manager.execute_brightness_test(
                **self.BRIGHTNESS_TEST_PARAMS
            )
            asserts.assert_true(
                initial == final,
                f"Brightness failed to return to its original level after adjustments."
                f"Initial: {initial}, Final: {final}"
            )
            logging.info("TEST PASSED: Brightness successfully adjusted and restored")

        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Brightness Test failed: %s", err)
            asserts.fail(f"Brightness Test execution failed: {err}")

    # 2. Screen Timeout testing
    def test_screen_timeouts(self):
        """Sequentially set, verifies the system settings and checks screen-off behaviour
        for all timeout options."""

        logging.info("=" * 60)
        logging.info("Starting Sequential Screen Timeout verification Test.")
        logging.info("=" * 60)

        try:
            self.test_manager.test_sequential_timeouts(self.TIMEOUT_CONFIGS)

            logging.info(
                "TEST PASSED: All sequential timeout verification completed successfully.")
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Timeout Test failed: %s", err)
            asserts.fail("Timeout Test execution failed.", {"error": str(err)})


if __name__ == "__main__":
    # Ensure the Mobly test runner is executed
    test_runner.main()