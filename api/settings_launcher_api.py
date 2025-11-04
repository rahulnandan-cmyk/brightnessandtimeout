#!/usr/bin/env python3
"""Settings Launcher API functions."""
import logging
import time

# Import the core manager
from utils.display_settings_manager1 import DisplaySettingsManager


class SettingsLauncherAPI:
    """API for settings launcher operations."""

    def __init__(self, manager: DisplaySettingsManager):
        self.manager = manager
        self.d = manager.d
        self._settings_package = "com.android.settings"

    def access_settings_from_launcher(self) -> bool:
        """Tests accessing the main Settings application from the app launcher."""
        logging.info("Attempting to launch the Android Settings application...")

        try:
            self.d.app_start(self._settings_package)
            time.sleep(3)

            current_pkg = self.d.info.get("currentPackageName", "")

            if current_pkg == self._settings_package:
                logging.info("SUCCESS: Settings app launched successfully via launcher.")
                return True

            logging.error("FAILURE: Expected '%s', but found '%s'.",
                          self._settings_package, current_pkg)
            return False

        except (RuntimeError, ValueError, OSError) as err:
            logging.error("Failed to launch Settings app: %s", err, exc_info=True)
            return False

    def verify_settings_ui_visible(self) -> bool:
        """
        Verifies that the Settings UI is visible and responsive.

        :returns: True if Settings UI elements are visible, False otherwise
        :rtype: bool
        """
        try:
            # Check if common Settings UI elements are present
            if self.d(textContains="Settings").exists or self.d(textContains="Search").exists:
                logging.info("Settings UI is visible and responsive")
                return True

            logging.warning("Settings UI elements not detected")
            return False
        except (RuntimeError, ValueError, OSError) as err:
            logging.error("Error verifying Settings UI: %s", err)
            return False
