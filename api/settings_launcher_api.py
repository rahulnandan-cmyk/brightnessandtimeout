#!/usr/bin/env python3
"""Settings Launcher API functions."""
import logging
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
            self.manager.access_settings_from_launcher()
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
      Uses the manager's utility method.
      """
        return self.manager.verify_settings_ui_visible()
