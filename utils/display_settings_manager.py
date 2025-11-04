#!/usr/bin/env python3
"""Module for managing and testing Android Display Settings (Brightness and Timeout)."""
import logging
import time
from typing import List, Tuple

import uiautomator2 as u2
from mobly import asserts
from mobly.controllers import android_device
from uiautomator2 import Device

class DisplaySettingsManager:
    """
    Manages all display-related test setup, execution (Brightness and Timeout),
    and teardown using UIAutomator2 and ADB shell commands.
    """

    # Constants
    HOME_KEYWORDS = ["launcher", "home"]
    DISPLAY_LABELS = [
        "Display",
        "Screen",
        "Screen & display",
        "Display & brightness",
        "Display settings",
    ]
    BRIGHTNESS_LABELS = ["Brightness level", "Adaptive brightness", "Brightness"]
    DEFAULT_TIMEOUT_MS = 30000
    SETTINGS_PACKAGE = "com.android.settings"

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d: Device = u2.connect(ad.serial)

        # Initial wake-up to ensure device is responsive
        try:
            for cmd in ["input keyevent KEYCODE_WAKEUP", "input keyevent KEYCODE_MENU"]:
                self.ad.adb.shell(cmd)
                time.sleep(0.5)
            logging.info("Initial wake-up commands sent successfully!")
        except Exception as e:
            logging.error("Initial device wake-up failed: %s", e)

    def setup_test(self) -> bool:
        """
        Set up the device for testing (wake, home screen, disable adaptive features).

        :returns: True if setup completed successfully, False otherwise.
        :rtype: bool
        """

        logging.info("=" * 60)
        logging.info("Starting Display Test Setup")
        logging.info("=" * 60)

        try:
            # Global setup for both brightness and timeout tests.
            self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")
            # Disable Adaptive Brightness.
            self.ad.adb.shell("settings put system screen_brightness_mode 0")

            self._wake_up_device()
            self._ensure_home_screen()
            logging.info("Test setup completed successfully")
            return True
        except Exception as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self) -> None:
        """
        Cleans up by resetting timeout to default (30s) and returning to the home screen
        """

        try:
            logging.info("Starting teardown - resetting settings and returning home")

            # Use _close_settings_dialogs for cleanup
            self._close_settings_dialogs()

            logging.info(
                "Resetting timeout to %d seconds...", self.DEFAULT_TIMEOUT_MS // 1000
            )
            self.ad.adb.shell(
                f"settings put system screen_off_timeout {self.DEFAULT_TIMEOUT_MS}"
            )

        except Exception as e:
            logging.error("Teardown failed: %s", e, exc_info=True)

    def _ensure_home_screen(self):
        """Forces the device to the home screen using multiple home presses."""
        logging.info("Ensuring Home Screen...")
        pkg = ""
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            logging.info("Current package: %s", pkg)
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                logging.info("Home screen detected: %s", pkg)
                return

        # 'pkg' is guaranteed to exist due to initialization or last assignment.
        raise RuntimeError(
            f"Home Screen not detected after 3 attempts. package: {pkg}"
        )

    def _wake_up_device(self):
        """Wakes up the device and dismisses the keyguard"""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _close_settings_dialogs(self):
        """Utility to close any open settings dialogs and returns to home."""
        logging.info("Closing any open settings...")
        # Press back multiple times.
        for _ in range(3):
            self.d.press("back")
            time.sleep(0.5)
        # Return to home
        self.d.press("home")
        time.sleep(1)

    def _scroll_and_click_setting(
            self, setting_labels: List[str], timeout: int = 2) -> None:
        """
        Scrolls the current view to find an element matching any of the given
        labels, clicks it, and raises an error if none are found.

        Args:
            setting_labels: A LIST of possible UI texts to search for (e.g., ["Display", "Screen"]).
            timeout: Seconds to sleep after clicking.
        """
        logging.info(
            "Attempting to find and click settings related to '%s'...", setting_labels
        )

        found_label = None

        # 1. Iterate through all possible labels, scrolling to find each one.
        for label in setting_labels:
            if self.d(scrollable=True).exists:
                # Scroll until the text is found.
                self.d(scrollable=True).scroll.to(textContains=label)

                # 2. Check if the element now exists in the viewport and click it.
            if self.d(textContains=label).exists:
                self.d(textContains=label).click()
                logging.info("Successfully clicked setting with label: '%s'.", label)
                found_label = label
                break

        # 3. Handle total failure if no label was found after all attempts.
        if found_label is None:
            # Error handling fallback: Collect visible options for debugging.
            options = [el.text for el in self.d.xpath("//*[@text]").all()]
            logging.error(
                "None of the required settings (%s) were found! Options: %s",
                setting_labels,
                options,
                exc_info=True,
            )
            raise RuntimeError(
                f"Could not find any of the required settings: {setting_labels}"
            )

        time.sleep(timeout)

    def _access_settings_from_launcher(self) -> None:
        """Starts the main Android Settings application."""
        logging.info("Starting Android Settings application...")
        # Use the class constant for consistency
        self.d.app_start(self.SETTINGS_PACKAGE)
        time.sleep(3)

    def _navigate_to_display_menu(self):
        """Navigates to the main Display Settings Menu."""
        logging.info("Navigating to Display Settings Menu...")

        # New Step: Start Settings App using the new helper method
        self._access_settings_from_launcher()

        found_display = False
        # 1. Try to find element if its visible without scrolling
        for label in self.DISPLAY_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info("Opened '%s' settings", label)
                found_display = True
                break

        if not found_display:
            # 2. Scrolling fallback
            # If this fails, the utility function will raise the RuntimeError.
            self._scroll_and_click_setting(setting_labels=self.DISPLAY_LABELS)

        time.sleep(2)

    def _navigate_to_brightness_settings(self):
        """Navigates from the Display menu to the brightness slider control."""
        self._navigate_to_display_menu()

        found_brightness = False
        # 1. Try to find the element if it's visible without scrolling
        for label in self.BRIGHTNESS_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info("Clicked brightness options: '%s'", label)
                found_brightness = True
                break

        if not found_brightness:
            # 2. Scrolling fallback: If the direct search fails, use the robust utility.
            self._scroll_and_click_setting(setting_labels=self.BRIGHTNESS_LABELS)

        time.sleep(2)

    def _open_timeout_settings(self):
        """Navigates from home to the Screen Timeout setting selection menu"""
        logging.info("Navigating to Screen Timeout Settings...")

        self._close_settings_dialogs()
        self._navigate_to_display_menu()

        # Scroll to screen timeout option.
        self._scroll_and_click_setting(setting_labels=["Screen timeout"])

    def _get_brightness(self) -> int:
        """Get current brightness using ADB shell"""
        try:
            result = self.ad.adb.shell("settings get system screen_brightness")
            result_str = (
                result.decode("utf-8").strip()
                if isinstance(result, bytes)
                else str(result).strip()
            )
            return int(result_str) if result_str.isdigit() else -1
        except Exception as e:
            logging.error("Failed to get brightness: %s", e)
            return -1

    def execute_brightness_test(
            self, right_press: int = 10, left_press: int = 10, delay: float = 1.0
    ) -> Tuple[int, int]:
        """
        Adjusts brightness up and down using DPAD and returns initial/final values

        :returns: A tuple containing the initial and final brightness levels.
        :rtype: Tuple[int, int]
        """
        logging.info("=" * 60)
        logging.info("Starting Brightness Adjustment Test")
        logging.info("=" * 60)

        try:
            self._navigate_to_brightness_settings()

            initial_brightness = self._get_brightness()
            logging.info("Initial brightness: %d", initial_brightness)

            # 1. Increasing brightness.
            logging.info("Increasing brightness (%d steps)", right_press)
            for i in range(right_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info("Right %d/%d -> Brightness: %d", i + 1, right_press, curr)

            # 2. Decreasing Brightness
            logging.info("Decreasing brightness (%d steps)", left_press)
            for i in range(left_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info("Left %d/%d -> Brightness: %d", i + 1, left_press, curr)

            final_brightness = self._get_brightness()
            logging.info("Final Brightness: %d", final_brightness)

            self._close_settings_dialogs()  # clean up the UI

            # Returns two values: initial and final brightness for assertion
            return initial_brightness, final_brightness
        except Exception as e:
            logging.error("Error during brightness test: %s", e, exc_info=True)
            self._close_settings_dialogs()  # Ensure cleanup even on failure
            raise

    def _get_current_timeout(self) -> int:
        """Retrieves the current screen off timeout value in millisecond via ADB"""
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = (
                result.decode("utf-8").strip()
                if isinstance(result, bytes)
                else str(result).strip()
            )
            return int(result_str) if result_str.isdigit() else 0

        except Exception as e:
            logging.error("Failed to get timeout: %s", e)
            return 0

    def _is_screen_off(self) -> bool:
        """Checks if the device screen is off (Asleep) using dumpsys power."""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state

        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def test_sequential_timeouts(self, timeout_labels: List[Tuple[str, int, int]]):
        """
        Tests sequential timeout options (clicks UI, verify settings, check screen-off).

        Args:
            timeout_labels: List of tuples (label, expected_ms, wait_sec).
                - label: UI text to click (eg; 15 seconds)
                - expected_ms: Excepted timeout values in milliseconds.
                - wait_sec: Seconds to wait for screen-off verification (0 to skip).
        """

        for label, expected_ms, wait_sec in timeout_labels:
            logging.info("=" * 60)
            logging.info("Testing timeout option: %s", label)
            logging.info("=" * 60)

            try:
                self._open_timeout_settings()

                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info("Selected timeout: %s", label)
                else:
                    # Collects all available options.
                    options = [el.text for el in self.d.xpath("//*[@text]").all()]
                    logging.warning(
                        "Timeout option '%s' not found. Available: %s ", label, options
                    )
                    continue

                time.sleep(2)

                # 1. Verify system setting is correct.
                current_timeout = self._get_current_timeout()
                if current_timeout != expected_ms:
                    logging.error(
                        "Timeout Mismatch! Expected %d, got %d",
                        expected_ms, current_timeout
                    )
                    asserts.fail(
                        f"Timeout set incorrect for label {label}:"
                        f"Expected {expected_ms}ms, got {current_timeout}ms"
                    )
                else:
                    logging.info("Timeout set correctly to %dms", expected_ms)

                # 2. Verify the screen-off behaviour.
                if wait_sec > 0:
                    logging.info("Waiting %ds for screen-off verification...", wait_sec)
                    time.sleep(wait_sec)
                    if self._is_screen_off():
                        logging.info("Screen turned off as expected(%s)", label)
                        self._wake_up_device()
                    else:
                        logging.warning(
                            "Screen still ON after ON %ds (%s)", wait_sec, label
                        )
                        asserts.fail(
                            f"Screen did not turn off after {wait_sec}s for timeout {label}."
                        )
                else:
                    logging.warning(
                        "Screen-off verification skipped (wait_sec=0) for (%s)", label
                    )
                    self.d.press("home")
                    time.sleep(2)

            except Exception as e:
                logging.error("Error testing timeout '%s': %s", label, e, exc_info=True)
                self.d.press("home")
                time.sleep(2)
                raise

    def access_settings_from_launcher(self) -> bool:
        """Tests accessing the main Settings application from the app launcher."""

        SETTINGS_PACKAGE = "com.android.settings"  # pylint: disable=invalid-name
        logging.info("Attempting to launch the Android Settings application...")

        try:
            # self.d is the UI Automator client inside the manager
            self.d.app_start(SETTINGS_PACKAGE)
            time.sleep(3) # Wait for the app to fully load

            current_pkg = self.d.info.get("currentPackageName", "")

            if current_pkg == SETTINGS_PACKAGE:
                logging.info("SUCCESS: Settings app launched successfully via launcher.")
                return True

            # Using lazy logging (%s) is preferred for performance
            logging.error("FAILURE: Expected '%s', but found '%s'.",
                          SETTINGS_PACKAGE, current_pkg)
            return False

        except Exception as err:
            logging.error("Failed to launch Settings app: %s", err, exc_info=True)
            return False


# Factory function for mobly
def create_display_settings_manager(ad: android_device.AndroidDevice,) -> DisplaySettingsManager:
    """Factory function to create a DisplaySettingsManager instance"""
    return DisplaySettingsManager(ad)