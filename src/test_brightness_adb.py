#!/usr/bin/env python3
# src/test_brightness_adb.py
"""Display Settings Test Utils"""
import sys
import os
import logging

# Add the parent directory to Python path to find utils module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

from utils.screenbrightness_utils import create_brightness_test


class DisplaySettingsTest(base_test.BaseTestClass):
    """Test to validate display settings using common utils"""

    BRIGHTNESS_TEST_PARAMS = {
        "right_presses": 10,
        "left_presses": 10,
        "delay": 1.0
    }

    def setup_class(self):
        """Minimal setup - just get device"""
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]
        self.test_manager = None

    def test_display_settings_workflow(self):
        """Main test - just call the test manager with parameters"""
        logging.info("=" * 60)
        logging.info("Starting Display Settings Test")
        logging.info("=" * 60)

        try:
            # Create test manager with our parameters
            self.test_manager = create_brightness_test(self.ad)

            # Setup (wake device + navigate to settings)
            if not self.test_manager.setup_test():
                asserts.fail("Test setup failed")

            # Execute brightness test with our parameters
            initial, final = self.test_manager.test_brightness_adjustment(
                **self.BRIGHTNESS_TEST_PARAMS
            )

            # Validate brightness change
            asserts.assert_true(
                initial == final,
                f"Brightness failed to return to its original level after adjustments."
                f" Initial: {initial}, Final: {final}"
            )

            logging.info("TEST PASSED: Brightness successfully adjusted")

        except Exception as e:
            logging.error("Test failed: %s", e)
            asserts.fail(f"Test execution failed: {e}")

    def teardown_class(self):
        """Cleanup via test manager"""
        if hasattr(self, 'test_manager') and self.test_manager:
            self.test_manager.teardown_test()


if __name__ == "__main__":
    test_runner.main()