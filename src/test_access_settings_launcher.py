#!/usr/bin/env python3
"""Targeted Test Suite for Display Settings: Access Settings from Launcher (TC_35)."""

import os
import sys
from typing import Optional
from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device

# Add the parent directory to Python path to find 'utils' module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import manager and factory function
# Assumes utils.display_settings_manager is the correct path
from utils.display_settings_manager import create_display_settings_manager, DisplaySettingsManager

# Import standard logging for Mobly compatibility (as user has done)
import logging

class AccessSettingsLauncherOnly(base_test.BaseTestClass):
    """Verifies the core functionality of launching the Settings application."""

    test_manager: Optional[DisplaySettingsManager] = None

    def setup_class(self):
        """Get the device and initialize the manager."""
        # 1. Register and get the Android device
        self.ad = self.register_controller(android_device)[0]

        # 2. Create the unified test manager instance, passing ONLY the device controller.
        # This fixes the AttributeError, as the factory only requires 'ad'.
        self.test_manager = create_display_settings_manager(self.ad)

        # The device wake-up is now handled inside the manager's __init__

    def teardown_class(self):
        """Final cleanup: User explicitly set to pass."""
        # If you were to add cleanup, you would call:
        # if self.test_manager:
        #     self.test_manager.reset_to_default_settings()
        pass

    def setup_test(self):
        """Per-test setup: Ensure the device is ready and at the home screen."""
        # Call the manager's setup routine, which includes the robust home screen check
        if not self.test_manager.setup_test():
            asserts.fail("Test manager setup failed: Could not ensure clean state.")

    def teardown_test(self):
        """Per-test teardown: Ensure the device returns to the home screen."""
        # Call the manager's cleanup method
        self.test_manager.teardown_test()

    # --- THE SINGLE, TARGETED TEST CASE (TC_35) ---
    def test_access_settings_from_launcher(self):
        """
        Verifies that the user can successfully launch the Settings application
        by calling the manager's method. (TC_35)
        """
        logging.info("=" * 60)
        logging.info("Starting TC_35: Verify Access to Settings App")
        logging.info("=" * 60)

        try:
            # Calls the manager's method (where the actual u2 logic resides)
            success = self.test_manager.access_settings_from_launcher()

            asserts.assert_true(
                success,
                "Failed to access the Android Settings application "
                "(com.android.settings) from the launcher."
            )

            logging.info("TEST PASSED: TC_35 Settings application launched successfully.")

        except Exception as err:
            logging.error("TC_35 Test failed: %s", err)
            asserts.fail(f"TC_35 execution failed: {err}")

if __name__ == "__main__":
    # Ensure the Mobly test runner is executed
    test_runner.main()
