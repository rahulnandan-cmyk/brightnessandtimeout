#!/usr/bin/env python3
# api/settings_search_api.py
"""API for settings launcher and search operations."""
import logging
import time

# Import the base manager class
from utils.display_settings_manager1 import DisplaySettingsManager


class SettingsSearchAPI:
    """
    API for settings launcher and search operations.

    This class encapsulates test procedures related to launching the Android
    Settings application and validating its internal search functionality.
    It relies on the low-level interactions provided by DisplaySettingsManager.
    """

    def __init__(self, manager: DisplaySettingsManager):
        """
        Initializes the SettingsSearchAPI.

        :param manager: An instance of DisplaySettingsManager providing
                        low-level device access (u2.Device and ADB).
        """
        self.manager = manager
        # Alias the uiautomator2 device object for convenient access
        self.d = manager.d

    # --- Public Test Methods ---

    def access_settings_from_launcher(self) -> bool:
        """
        Tests accessing the main Settings application from the app launcher.

        Procedure:
        1. Launches the Settings application using the package name.
        2. Verifies that the current active package matches the expected settings package.

        :returns: True if the Settings app was launched successfully, False otherwise.
        """
        logging.info("Testing Settings Launcher Access")

        self.manager.access_settings_from_launcher()
        time.sleep(3)  # Wait for the application to fully load

        current_pkg = self.d.info.get("currentPackageName", "")
        # Compare the current package name to the expected settings package
        success = current_pkg == self.manager.SETTINGS_PACKAGE

        if success:
            logging.info("SUCCESS: Settings app launched successfully")
        else:
            logging.error("FAILED: Expected '%s', but found '%s'",
                          self.manager.SETTINGS_PACKAGE, current_pkg)
        return success

    def verify_settings_ui_visible(self) -> bool:
        """
        Verifies that the Settings UI is visible and responsive.

        This delegates the check to the underlying DisplaySettingsManager.

        :returns: True if key Settings UI elements are detected, False otherwise.
        """
        return self.manager.verify_settings_ui_visible()

    def test_search_nonexistent_term(self, search_term: str = "xyzabc123") -> bool:
        """
        Tests search functionality with a term that doesn't exist in settings.

        Test Procedure:
        1. Open the Settings app.
        2. Click the 'Search settings' bar.
        3. Enter a non-existent search term.
        4. Verify that the "No results found" message is displayed.

        :param search_term: The term to search for (default is a nonsense string).
        :returns: True if the "No results found" message is successfully displayed.
        """
        logging.info("Testing Search with Non-Existent Term: '%s'", search_term)

        try:
            # Step 1: Open Settings app
            self.manager.access_settings_from_launcher()
            time.sleep(3)

            # Step 2: Find and click search box (relying on the robust manager method)
            self.manager.scroll_and_click_setting(setting_labels=["Search settings", "Search"])
            time.sleep(1)

            # Step 3: Enter non-existent search term using u2's set_text
            self.d.send_keys(search_term)
            time.sleep(2)

            # Step 4: Verify "No results found" message
            no_results_found = self._verify_no_results_message()

            if no_results_found:
                logging.info("SUCCESS: 'No results found' message displayed correctly")
            else:
                logging.error("FAILED: 'No results found' message not displayed")

            # Clean up by closing the settings
            self.manager.close_settings_dialogs()
            return no_results_found

        # Combined Runtime and OS errors into one block for cleaner structure.
        except (RuntimeError, OSError) as e:
            logging.error("Search test failed with error: %s", e)
            self.manager.close_settings_dialogs()
            return False

    def navigate_to_settings_via_search(self) -> bool:
        """
        Navigates to the Settings app.

        Uses the same direct approach that works in other tests.
        """
        logging.info("Navigating to Settings app...")
        try:
            # Use the same approach that works in test_settings_launcher
            self.manager.access_settings_from_launcher()
            time.sleep(3)

            # Verify success
            current_pkg = self.d.info.get("currentPackageName", "")
            success = current_pkg == self.manager.SETTINGS_PACKAGE

            if success:
                logging.info("SUCCESS: Settings launched successfully")
            else:
                logging.error("FAILED: Settings app not launched. Current package: %s", current_pkg)

            return success

        except (RuntimeError, OSError) as e:
            logging.error("Failed to navigate to Settings: %s", e)
            return False

    # --- Private Helper Methods ---

    def _verify_no_results_message(self) -> bool:
        """
        Helper method to verify that the 'No results found' message is displayed
        in the current Settings search view.

        It uses the manager's scroll and click utility, which raises a
        RuntimeError if the element is not found, to detect success/failure.

        :returns: True if the 'No results found' message (or variation) is visible, False otherwise.
        """
        no_results_messages = ["No results for", "No results found"]
        # Add a common "no results" label to the list for robustness

        try:
            # Try to find the message using the robust scroll/click utility.
            # If found, the utility clicks it (which is acceptable here) and returns successfully.
            self.manager.scroll_and_click_setting(setting_labels=no_results_messages, timeout=0)
            return True  # Message found
        except RuntimeError:
            # If the manager raises RuntimeError, none of the messages were found.
            return False
        # Combined Runtime and OS errors into one block for cleaner structure.
        except OSError as e:
            logging.error("OS error verifying no results message: %s", e)
            return False
