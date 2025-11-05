#!/usr/bin/env python3
# display_settings_manager.py
import logging
import time
import uiautomator2 as u2
from typing import Tuple, List
from mobly import asserts
from mobly.controllers import android_device


class DisplaySettingsManager:
    """
    Manages all display-related test setup, execution (Brightness and Timeout),
    and teardown using UIAutomator2 and ADB shell commands.

    :param ad: The mobly Android controller instance

    **Attributes**
        - HOME_KEYWORDS(List[str]): Keywords used to identify the Android home screen package.
        - DISPLAY_LABELS(List[str]): UI labels used to locate the main display settings menu.
        - BRIGHTNESS_LABELS(List[str]): UI labels used to locate the brightness settings menu.
        - DEFAULT_TIMEOUT_MS(int): Default screen off timeout value in milliseconds (3000ms).
        - ad (android_device.AndroidDevice): The Mobly Android device handle.
        - d (uiautomator2.client): The UIautomator2 client instance connected to the device.


    **Methods**
        - setup_test(): prepares the device for testing.
        - teardown_test(): Reset settings and cleans up the device state.
        - execute_brightness_test(): Performs the brightness adjustment cycle test.
        - test_sequential_timeouts(): Tests multiple screen off timeout values.
    """

    # Constants
    HOME_KEYWORDS = ["launcher", "home"]
    DISPLAY_LABELS = ["Display", "Screen", "Screen & display", "Display & brightness",
                      "Display settings"]
    BRIGHTNESS_LABELS = ["Brightness level", "Adaptive brightness", "Brightness"]
    DEFAULT_TIMEOUT_MS = 30000

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        # Type hint added for self.d
        self.d: Device = u2.connect(ad.serial)

        # Initial wake-up to ensure device is response
        try:
            for cmd in ["input keyevent KEYCODE_WAKEUP", "input keyevent KEYCODE_MENU"]:
                self.ad.adb.shell(cmd)
                time.sleep(0.5)
            logging.info("Initial wake-up commands sent successfully!")
        except Exception as e:
            logging.error(f"Initial device wake-up failed: {e}")

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
            logging.error(f"Test setup failed: {e}", exc_info=True)
            return False


    def teardown_test(self) -> None:
        """
        Cleans up by resetting timeout to default (30s) and returning to the home screen
        """

        try:
            logging.info("Starting teardown - resetting settings and returning home")

            # Use _close_settings_dialogs for cleanup
            self._close_settings_dialogs()

            # Reset timeout to default
            logging.info(f"Resetting timeout to {self.DEFAULT_TIMEOUT_MS // 1000} seconds...")
            self.ad.adb.shell(f"settings put system screen_off_timeout {self.DEFAULT_TIMEOUT_MS}")

        except Exception as e:
            logging.error(f"Teardown failed:{e}", exc_info=True)

    def _ensure_home_screen(self):
        """Forces the device to the home screen using multiple home presses."""
        logging.info("Ensuring Home Screen...")
        pkg = ""
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            logging.info(f"Current package: {pkg}")
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                logging.info(f"Home screen detected:{pkg}")
                return

        # 'pkg' is guaranteed to exist due to initialization or last assignment.
        raise RuntimeError(f"Home Screen not detected after 3 attempts."
                           f"package: {pkg}")

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

    def _scroll_and_click_setting(self, setting_labels: List[str], timeout: int = 2) -> None:
        """
        Scrolls the current view to find an element matching any of the given
        labels, clicks it, and raises an error if none are found.

        Args:
            setting_labels: A LIST of possible UI texts to search for (e.g., ["Display", "Screen"]).
            timeout: Seconds to sleep after clicking.
        """
        logging.info(f"Attempting to find and click settings related to  '{setting_labels}'...")

        found_label = None

        # 1. Iterate through all possible labels, scrolling to find each one.
        for label in setting_labels:
            if self.d(scrollable=True).exists:
                # Scroll until the text is found.
                self.d(scrollable=True).scroll.to(textContains=label)

                # 2. Check if the element now exists in the viewport and click it.
            if self.d(textContains=label).exists:
                self.d(textContains=label).click()
                logging.info(f"Successfully clicked setting with label: '{label}'.")
                found_label = label
                break

        # 3. Handle total failure if no label was found after all attempts.
        if found_label is None:
            # Error handling fallback: Collect visible options for debugging.
            options = [el.text for el in self.d.xpath('//*[@text]').all()]
            logging.error(f"None of the required settings ({setting_labels}) "
                          f"were found! Options: {options}", exc_info=True)
            raise RuntimeError(f"Could not find any of the required settings: {setting_labels}")

        time.sleep(timeout)


    def _navigate_to_display_menu(self):
        """Navigates to the main Display Settings Menu."""
        logging.info("Navigating to Display Settings Menu...")
        self.d.app_start("com.android.settings")
        time.sleep(3)

        found_display = False
        # 1. Try to find element if its visible without scrolling
        for label in self.DISPLAY_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info(f"Opened '{label}' settings")
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
                logging.info(f"Clicked brightness options: '{label}'")
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
            result_str = result.decode('utf-8').strip() \
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else -1
        except Exception as e:
            logging.error(f"Failed to get brightness:{e}")
            return -1

    def execute_brightness_test(self, right_press: int = 10, left_press: int = 10,
                                delay: float = 1.0) -> Tuple[int, int]:
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
            logging.info(f"Initial brightness: {initial_brightness}")

            # 1. Increasing brightness.
            logging.info(f"Increasing brightness ({right_press} steps)")
            for i in range(right_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info(f"Right {i+1}/{right_press} -> Brightness: {curr}")

            # 2. Decreasing Brightness
            logging.info(f"Decreasing brightness ({left_press} steps)")
            for i in range(left_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info(f"Left {i+1}/{left_press} -> Brightness:{curr}")

            final_brightness = self._get_brightness()
            logging.info(f"Final Brightness: {final_brightness}")

            self._close_settings_dialogs() # clean up the UI

            # Returns two values: initial and final brightness for assertion
            return initial_brightness, final_brightness

        except Exception as e:
            logging.error(f"Error during brightness test: {e}", exc_info=True)
            self._close_settings_dialogs() # Ensure cleanup even on failure
            raise

    def _get_current_timeout(self) -> int:
        """Retrieves the current screen off timeout value in millisecond via ADB"""
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = result.decode('utf-8').strip() \
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else 0

        except Exception as e:
            logging.error(f"Failed to get timeout: {e}")
            return 0

    def _is_screen_off(self) -> bool:
        """Checks if the device screen is off (Asleep) using dumpsys power."""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state

        except Exception as e:
            logging.error(f"Failed to check screen state: {e}")
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
            logging.info(f"Testing timeout option: {label}")
            logging.info("=" * 60)

            try:
                self._open_timeout_settings()

                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info(f"Selected timeout: {label}")
                else:
                    # Collects all available options.
                    options = [el.text for el in self.d.xpath('//*[@text]').all()]
                    logging.warning(f"Timeout option '{label}' not found. Available: {options} ")
                    continue

                time.sleep(2)

                # 1. Verify system setting is correct.
                current_timeout = self._get_current_timeout()
                if current_timeout != expected_ms:
                    logging.error(f"Timeout Mismatch! Expected {expected_ms}, got {current_timeout}")
                    asserts.fail(f"Timeout set incorrect for label {label}:"
                                 f"Expected {expected_ms}ms, got {current_timeout}ms")
                else:
                    logging.info(f"Timeout set correctly to {expected_ms}ms")

                # 2. Verify the screen-off behaviour.
                if wait_sec > 0:
                    logging.info(f"Waiting {wait_sec}s for screen-off verification...")
                    time.sleep(wait_sec)
                    if self._is_screen_off():
                        logging.info(f"Screen turned off as expected({label})")
                        self._wake_up_device()
                    else:
                        logging.warning(f"Screen still ON after ON {wait_sec}s ({label})")
                        asserts.fail(f"Screen did not turn off after {wait_sec}s for timeout {label}.")
                else:
                    logging.warning(f"Screen-off verification skipped (wait_sec=0) for ({label})")
                    self.d.press("home")
                    time.sleep(2)

            except Exception as e:
                logging.error(f"Error testing timeout'{label}': {e}", exc_info=True)
                self.d.press("home")
                time.sleep(2)
                raise

# Factory function for mobly
def create_display_settings_manager(ad: android_device.AndroidDevice) -> DisplaySettingsManager:
    """Factory function to create a DisplaySettingsManager instance"""
    return DisplaySettingsManager(ad)
