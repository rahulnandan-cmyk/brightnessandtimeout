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

    :param ad: The Mobly AndroidDevice controller instance.

    **Attributes**
        - HOME_KEYWORDS (List[str]): Keywords used to identify the Android home screen package.
        - DISPLAY_LABELS (List[str]): UI labels used to locate the main Display settings menu.
        - BRIGHTNESS_LABELS (List[str]): UI labels used to locate the brightness settings menu.
        - DEFAULT_TIMEOUT_MS (int): Default screen off timeout value in milliseconds (30000 ms).
        - ad (android_device.AndroidDevice): The Mobly Android device handle.
        - d (uiautomator2.client): The UIAutomator2 client instance connected to the device.

    **Methods**
        - setup_test(): Prepares the device for testing.
        - teardown_test(): Resets settings and cleans up the device state.
        - execute_brightness_test(): Performs the brightness adjustment cycle test.
        - test_sequential_timeouts(): Tests multiple screen off timeout values.
    """

    HOME_KEYWORDS = ["launcher", "home"]
    DISPLAY_LABELS = [
        "Display", "Screen", "Screen & display", "Display & brightness", "Display settings"
    ]
    BRIGHTNESS_LABELS = ["Brightness level", "Adaptive brightness", "Brightness"]
    DEFAULT_TIMEOUT_MS = 30000

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d = u2.connect(ad.serial)

        # Initial wake-up to ensure device is responsive.
        try:
            for cmd in ["input keyevent KEYCODE_WAKEUP", "input keyevent KEYCODE_MENU"]:
                self.ad.adb.shell(cmd)
                time.sleep(0.5)
            logging.info("Initial wake-up commands sent successfully")
        except Exception as e:
            logging.error(f"Initial device wake-up failed: {e}")

    # ===============================================
    # SETUP & TEARDOWN METHODS
    # ===============================================

    def setup_test(self) -> bool:
        """
        Sets up the device for testing (wake, home screen, disable adaptive features).

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
        Cleans up by resetting timeout to default (30s) and returning to the home screen.
        """
        try:
            logging.info("Starting teardown - resetting settings and returning home...")

            # Use three back presses to dismiss dialogs.
            for _ in range(3):
                self.d.press("back")
                time.sleep(0.5)
            self.d.press("home")
            time.sleep(1)

            # Reset timeout to default.
            logging.info(f"Resetting timeout to {self.DEFAULT_TIMEOUT_MS // 1000} seconds...")
            self.ad.adb.shell(f"settings put system screen_off_timeout {self.DEFAULT_TIMEOUT_MS}")

        except Exception as e:
            logging.error(f"Teardown failed: {e}", exc_info=True)

    def _ensure_home_screen(self):
        """Forces the device to the home screen using multiple home presses."""
        logging.info("Ensuring Home screen...")
        pkg = ""
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            logging.info(f"Current package: {pkg}")
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                logging.info(f"Home screen detected: {pkg}")
                return

        # 'pkg' is guaranteed to exist due to initialization or last assignment.
        raise RuntimeError(f"Home screen not detected after 3 attempts. Package: {pkg}")

    def _wake_up_device(self):
        """Wakes up the device and dismisses the keyguard."""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _close_settings_dialogs(self):
        """Utility to close any open settings dialogs and return to home."""
        logging.info("Closing any open dialogs...")
        # Press back multiple times.
        for _ in range(3):
            self.d.press("back")
            time.sleep(0.5)
        # Return to home.
        self.d.press("home")
        time.sleep(1)

    # ===============================================
    # NAVIGATION METHODS
    # ===============================================

    def _navigate_to_display_menu(self):
        """Navigates to the main Display Settings menu (coordinate-free)."""
        logging.info("Navigating to Display Settings menu...")
        self.d.app_start("com.android.settings")
        time.sleep(3)

        found_display = False
        for label in self.DISPLAY_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info(f"Opened '{label}' settings")
                found_display = True
                break

        if not found_display:
            # Scrolling fallback.
            if self.d(scrollable=True).exists:
                self.d(scrollable=True).scroll.to(textContains="Display")

            for label in self.DISPLAY_LABELS:
                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info(f"Opened '{label}' settings after scrolling")
                    found_display = True
                    break

        if not found_display:
            # Collects all UI text for error reporting.
            options = [el.text for el in self.d.xpath('//*[@text]').all()]
            logging.error(f"Could not find Display section! Available Settings options: {options}")
            raise RuntimeError("Could not find 'Display' in Settings")

        time.sleep(2)

    def _navigate_to_brightness_settings(self):
        """Navigates from the Display menu to the brightness slider control."""
        self._navigate_to_display_menu()

        found_brightness = False
        for label in self.BRIGHTNESS_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info(f"Clicked brightness option: '{label}'")
                found_brightness = True
                break

        if not found_brightness:
            if self.d(scrollable=True).exists:
                self.d(scrollable=True).scroll.to(textContains="Brightness")

            if self.d(textContains="Brightness").exists:
                self.d(textContains="Brightness").click()
                logging.info("Clicked 'Brightness' after scrolling")
            else:
                raise RuntimeError("Could not find any 'Brightness' option in Settings.")

        time.sleep(2)

    def _open_timeout_settings(self):
        """Navigates from home to the Screen Timeout setting selection menu."""
        logging.info("Navigating to Screen Timeout settings...")

        self._close_settings_dialogs()
        self._navigate_to_display_menu()

        # Scroll to Screen timeout option.
        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(textContains="Screen timeout")

        if self.d(textContains="Screen timeout").exists:
            self.d(textContains="Screen timeout").click()
            logging.info("Opened 'Screen timeout' menu")
        else:
            # Collects all UI text for error reporting.
            options = [el.text for el in self.d.xpath('//*[@text]').all()]
            logging.error(f"'Screen timeout' menu not found! Options: {options}")
            raise RuntimeError("Could not find 'Screen timeout' option")

        time.sleep(2)

    # ===============================================
    # BRIGHTNESS TEST LOGIC
    # ===============================================

    def _get_brightness(self) -> int:
        """
        Get current screen brightness level using ADB shell.

        :returns: The current brightness level (0-255 range) or -1 on error.
        :rtype: int
        """
        try:
            result = self.ad.adb.shell("settings get system screen_brightness")
            result_str = result.decode('utf-8').strip() \
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else -1
        except Exception as e:
            logging.error(f"Failed to get brightness: {e}")
            return -1

    def execute_brightness_test(self, right_presses: int = 10, left_presses: int = 10, delay: float = 1.0) -> Tuple[int, int]:
        """
        Adjusts brightness up and down using DPAD keys and returns initial/final values.

        The test verifies symmetry by checking if the brightness returns to the
        original level after equal UP and DOWN steps.

        :param right_presses: Number of KEYCODE_DPAD_RIGHT presses (brightness up).
        :type right_presses: int
        :param left_presses: Number of KEYCODE_DPAD_LEFT presses (brightness down).
        :type left_presses: int
        :param delay: Time in seconds to wait between key presses.
        :type delay: float
        :returns: A tuple containing the (initial brightness, final brightness).
        :rtype: Tuple[int, int]
        """
        logging.info("=" * 60)
        logging.info("Starting Brightness Adjustment Test")
        logging.info("=" * 60)

        try:
            self._navigate_to_brightness_settings()

            initial_brightness = self._get_brightness()
            logging.info(f"Initial brightness: {initial_brightness}")

            # Adjustment UP (DPAD_RIGHT).
            logging.info(f"Adjusting UP ({right_presses} steps)")
            for i in range(right_presses):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info(f"UP {i+1}/{right_presses} -> Brightness: {curr}")

            # Adjustment DOWN (DPAD_LEFT).
            logging.info(f"Adjusting DOWN ({left_presses} steps)")
            for i in range(left_presses):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info(f"DOWN {i+1}/{left_presses} -> Brightness: {curr}")

            final_brightness = self._get_brightness()
            logging.info(f"Final brightness: {final_brightness}")

            self.d.press("home")
            time.sleep(1)

            # Returns two values: initial and final brightness for assertion.
            return initial_brightness, final_brightness

        except Exception as e:
            logging.error(f"Error during brightness test: {e}", exc_info=True)
            self.d.press("home")
            time.sleep(1)
            raise

    # ===============================================
    # TIMEOUT TEST LOGIC
    # ===============================================

    def _get_current_timeout(self) -> int:
        """
        Retrieves the current screen off timeout value in milliseconds via ADB.

        :returns: The current timeout value in milliseconds, or 0 on error.
        :rtype: int
        """
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = result.decode('utf-8').strip()\
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else 0
        except Exception as e:
            logging.error(f"Failed to get timeout: {e}")
            return 0

    def _is_screen_off(self) -> bool:
        """
        Checks if the device screen is off (Asleep) using dumpsys power.

        :returns: True if the screen is off (Asleep), False otherwise.
        :rtype: bool
        """
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state
        except Exception as e:
            logging.error(f"Failed to check screen state: {e}")
            return False

    def test_sequential_timeouts(self, timeout_labels: List[Tuple[str, int, int]]):
        """
        Tests sequential timeout options (click UI, verify setting, check screen-off).

        :param timeout_labels: List of tuples (label, expected_ms, wait_sec).
            - label: UI text to click (e.g., "15 seconds").
            - expected_ms: Expected timeout value in milliseconds.
            - wait_sec: Seconds to wait for screen-off verification (0 to skip).
        :type timeout_labels: List[Tuple[str, int, int]]
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
                    logging.warning(f"Timeout option '{label}' not found. Available: {options}")
                    continue  # Move to the next timeout test

                time.sleep(2)

                # 1. Verify system setting is correct.
                current_timeout = self._get_current_timeout()
                if current_timeout != expected_ms:
                    logging.error(f"Timeout mismatch! Expected {expected_ms}, got {current_timeout}")
                    asserts.fail(f"Timeout set incorrectly for {label}: Expected {expected_ms}ms, got {current_timeout}ms")
                else:
                    logging.info(f"Timeout set correctly to {expected_ms} ms")

                # 2. Verify screen-off behavior.
                if wait_sec > 0:
                    logging.info(f"Waiting {wait_sec}s for screen-off verification...")
                    time.sleep(wait_sec)
                    if self._is_screen_off():
                        logging.info(f"Screen turned off as expected ({label})")
                        self._wake_up_device()
                    else:
                        logging.warning(f"Screen still ON after {wait_sec}s ({label})")
                        asserts.fail(f"Screen did not turn off after {wait_sec}s for timeout {label}.")
                else:
                    logging.info(f"Screen-off verification skipped (wait_sec=0) for {label}")

                self.d.press("home")
                time.sleep(1)

            except Exception as e:
                logging.error(f"Error testing timeout '{label}': {e}", exc_info=True)
                self.d.press("home")
                time.sleep(1)
                raise


# Factory function for Mobly
def create_display_settings_manager(ad: android_device.AndroidDevice) -> DisplaySettingsManager:
    """
    Factory function to create a DisplaySettingsManager instance.

    :param ad: The Mobly AndroidDevice controller instance.
    :type ad: android_device.AndroidDevice
    :returns: An instance of DisplaySettingsManager.
    :rtype: DisplaySettingsManager
    """
    return DisplaySettingsManager(ad)
