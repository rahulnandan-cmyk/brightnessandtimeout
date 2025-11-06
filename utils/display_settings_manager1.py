#!/usr/bin/env python3
# src/test_mobly_api.py
"""Example test using the new API structure."""
import os
import sys
import logging
from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import core manager and APIs
from utils.display_settings_manager import create_display_settings_manager
from api.brightness_api import BrightnessAPI
from api.timeout_api import TimeoutAPI
from api.settings_launcher_api import SettingsLauncherAPI


class TestChromebookSettings(base_test.BaseTestClass):
    """Test using the new API structure."""

    def __init__(self, configs):
        """Initialize test class with proper attribute declaration."""
        super().__init__(configs)
        self.ad = None
        self.manager = None
        self.brightness_api = None
        self.timeout_api = None
        self.launcher_api = None

    def setup_class(self):
        """Get the device and initialize all APIs."""
        # Setup device and APIs
        self.ad = self.register_controller(android_device)[0]
        self.manager = create_display_settings_manager(self.ad)
        self.launcher_api = SettingsLauncherAPI(self.manager)
        self.brightness_api = BrightnessAPI(self.manager)
        self.timeout_api = TimeoutAPI(self.manager)

    def setup_test(self):
        """Per-test setup."""
        if not self.manager.setup_test():
            asserts.fail("Test manager setup failed")

    def teardown_test(self):
        """Per-test teardown."""
        self.manager.teardown_test()

    def test_settings_launcher(self):
        """Test settings launcher using API."""
        success = self.launcher_api.access_settings_from_launcher()
        asserts.assert_true(success, "Should launch settings successfully")

    def test_brightness_adjustment(self):
        """Test brightness adjustment using API."""
        initial, final = self.brightness_api.execute_brightness_test(
            right_press=5, left_press=6, delay=0.5
        )

        # Use the variables to avoid unused variable warnings
        asserts.assert_is_instance(initial, int, "Initial brightness should be integer")
        asserts.assert_is_instance(final, int, "Final brightness should be integer")
        logging.info("Brightness changed from %d to %d", initial, final)

    def test_timeout_settings(self):
        """Test timeout settings using API."""
        timeout_labels = [
            ("15 seconds", 15000, 20),
            ("30 seconds", 30000, 35),
        ]
        self.timeout_api.test_sequential_timeouts(timeout_labels)

if __name__ == "__main__":
    test_runner.main()
