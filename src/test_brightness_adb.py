#!/usr/bin/env python3
"""Display Settings Test - Simplified with Common Utils"""
import logging
from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

from utils.common_utils import create_display_test


class DisplaySettingsTest(base_test.BaseTestClass):
    """Test to validate display settings using common utils"""

    # Test parameters - just define these!
    COORDINATES = {
        "win_button": (20, 1055),
        "settings": (296, 577),
        "display": (242, 955),
        "brightness": (178, 321),
    }

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
            self.test_manager = create_display_test(self.ad, self.COORDINATES)

            # Setup (wake device + navigate to settings)
            if not self.test_manager.setup_test():
                asserts.fail("Test setup failed")

            # Execute brightness test with our parameters
            initial, final, values = self.test_manager.execute_brightness_test(
                **self.BRIGHTNESS_TEST_PARAMS
            )

            # Simple assertion
            asserts.assert_true(
                initial != final,
                f"Brightness should change. Initial: {initial}, Final: {final}"
            )

            logging.info("✓ TEST PASSED: Brightness successfully adjusted")

        except Exception as e:
            logging.error("Test failed: %s", e)
            asserts.fail(f"Test execution failed: {e}")

    def teardown_class(self):
        """Cleanup via test manager"""
        if hasattr(self, 'test_manager') and self.test_manager:
            self.test_manager.teardown_test()


if __name__ == "__main__":
    test_runner.main()