#!/usr/bin/env python3
# src/test_mobly_api.py
"""Mobly API Testing"""
import os
import sys
import logging

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

# Add the parent directory to Python path before local application imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Application/Local Imports
from api.brightness_api import BrightnessAPI
from api.dark_theme_api import DarkThemeAPI
from api.settings_launcher_api import SettingsLauncherAPI
from api.settings_search_api import SettingsSearchAPI
from api.timeout_api import TimeoutAPI

from utils.display_settings_manager1 import create_display_settings_manager


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
        self.settings_search_api = None

    def setup_class(self):
        """Get the device and initialize all APIs."""
        # Setup device and APIs
        self.ad = self.register_controller(android_device)[0]
        self.manager = create_display_settings_manager(self.ad)
        self.launcher_api = SettingsLauncherAPI(self.manager)
        self.brightness_api = BrightnessAPI(self.manager)
        self.timeout_api = TimeoutAPI(self.manager)
        self.dark_theme_api = DarkThemeAPI(self.manager)
        self.settings_search_api = SettingsSearchAPI(self.manager)

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

        asserts.assert_is_instance(
            initial, int, "Initial brightness should be integer"
        )
        asserts.assert_is_instance(
            final, int, "Final brightness should be integer"
        )
        logging.info("Brightness changed from %d to %d", initial, final)

    def test_timeout_settings(self):
        """Test timeout settings using API."""
        timeout_labels = [
            ("15 seconds", 15000, 20),
            ("30 seconds", 30000, 35),
        ]
        self.timeout_api.test_sequential_timeouts(timeout_labels)

    def test_complete_dark_theme_functionality(self):
        """
        TC_29: Complete dark theme functionality test in one function.
        """
        logging.info("=" * 60)
        logging.info("TC_29: Complete Dark Theme Functionality Test")
        logging.info("=" * 60)

        # Test all dark theme functionality sequentially
        test_functions = [
            ("Toggle Enable",
             lambda: self.dark_theme_api.toggle_dark_theme(enable=True)),
            ("Toggle Disable",
             lambda: self.dark_theme_api.toggle_dark_theme(enable=False)),
            ("Sunset Schedule",
             self.dark_theme_api.test_sunset_sunrise_schedule),
            ("Custom Schedule",
             lambda: self.dark_theme_api.test_custom_time_schedule("21:00")),
            ("Disable Schedule (None)",
             self.dark_theme_api.disable_dark_theme_schedule)
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
            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.error("%s: ERROR - %s", test_name, e, exc_info=True)
                all_passed = False

        final_result = "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"
        asserts.assert_true(
            all_passed,
            f"Dark theme test flow failed. Final Result: {final_result}"
        )
        logging.info("Final Result: %s", final_result)

    # def test_settings_ui_visibility(self):
    #     """Test that Settings UI is visible."""
    #     success = self.launcher_api.verify_settings_ui_visible()
    #     asserts.assert_true(success, "Settings UI should be visible")

    def test_search_nonexistent_term(self):
        """Test search functionality with non-existent term."""
        self.launcher_api.access_settings_from_launcher()
        success = self.settings_search_api.test_search_nonexistent_term(
            "xyzabc123"
        )
        asserts.assert_true(
            success,
            "Should display 'No results found' for non-existent term"
        )

    def test_navigate_settings_via_search(self):
        """Test navigating to Settings via device search."""
        success = self.settings_search_api.navigate_to_settings_via_search()
        asserts.assert_true(
            success,
            "Should navigate to Settings via search successfully"
        )

if __name__ == "__main__":
    test_runner.main()
