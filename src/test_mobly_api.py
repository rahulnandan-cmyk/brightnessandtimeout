#!/usr/bin/env python3
# src/test_mobly_api.py
"""Mobly API Testing"""
import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

# Import core manager and APIs
from utils.display_settings_manager1 import create_display_settings_manager
from api.brightness_api import BrightnessAPI
from api.timeout_api import TimeoutAPI
from api.settings_launcher_api import SettingsLauncherAPI
from api.dark_theme_api import DarkThemeAPI


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
        self.dark_theme_api = None

    def setup_class(self):
        """Get the device and initialize all APIs."""
        # Setup device and APIs
        self.ad = self.register_controller(android_device)[0]
        self.manager = create_display_settings_manager(self.ad)
        self.launcher_api = SettingsLauncherAPI(self.manager)
        self.brightness_api = BrightnessAPI(self.manager)
        self.timeout_api = TimeoutAPI(self.manager)
        self.dark_theme_api = DarkThemeAPI(self.manager)

    def setup_test(self):
        """Per-test setup."""
        if not self.manager.setup_test():
            asserts.fail("Test manager setup failed")

    def teardown_test(self):
        """Per-test teardown."""
        self.manager.teardown_test()

    # def test_settings_launcher(self):
    #     """Test settings launcher using API."""
    #     success = self.launcher_api.access_settings_from_launcher()
    #     asserts.assert_true(success, "Should launch settings successfully")

    # def test_brightness_adjustment(self):
    #     """Test brightness adjustment using API."""
    #     initial, final = self.brightness_api.execute_brightness_test(
    #         right_press=5, left_press=6, delay=0.5
    #     )
    #
    #     asserts.assert_is_instance(initial, int, "Initial brightness should be integer")
    #     asserts.assert_is_instance(final, int, "Final brightness should be integer")
    #     logging.info("Brightness changed from %d to %d", initial, final)
    #
    # def test_timeout_settings(self):
    #     """Test timeout settings using API."""
    #     timeout_labels = [
    #         ("15 seconds", 15000, 20),
    #         ("30 seconds", 30000, 35),
    #     ]
    #     self.timeout_api.test_sequential_timeouts(timeout_labels)
    #



    def test_complete_dark_theme_functionality(self):
        """
        TC_29: Complete dark theme functionality test in one function.
        """
        logging.info("=" * 60)
        logging.info("TC_29: Complete Dark Theme Functionality Test")
        logging.info("=" * 60)

        # Test all dark theme functionality sequentially
        test_functions = [
            ("Toggle Enable", lambda: self.dark_theme_api.toggle_dark_theme(enable=True)),
            ("Toggle Disable", lambda: self.dark_theme_api.toggle_dark_theme(enable=False)),
            # ("Sunset Schedule", self.dark_theme_api.test_sunset_sunrise_schedule),
            # ("Custom Schedule", lambda: self.dark_theme_api.test_custom_time_schedule("21:00")),
            # ("Complete Flow", self.dark_theme_api.complete_dark_theme_test_flow)
        ]

        all_passed = True

        for test_name, test_func in test_functions:
            logging.info(" Testing %s...", test_name)
            try:
                result = test_func()
                if result:
                    logging.info("%s: PASSED", test_name)
                else:
                    logging.error("%s: FAILED", test_name)
                    all_passed = False
            except Exception as e:
                logging.error("%s: ERROR - %s", test_name, e)
                all_passed = False

        asserts.assert_true(all_passed, "All dark theme tests should pass")
        logging.info("Final Result: %s", "ALL TESTS PASSED"
        if all_passed else "SOME TESTS FAILED")

if __name__ == "__main__":
    test_runner.main()
