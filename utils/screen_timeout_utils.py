#!/usr/bin/env python3
# utils/screen_timeout_utils.py
import logging
import time
import uiautomator2 as u2
from typing import Tuple, List, Dict, Any, Optional

from PyQt5.QtWidgets import QScrollArea
# Mobly imports
from  mobly import asserts, base_test
from mobly.controllers import android_device

class TimeoutTestManager:
    """Manages screen timeout test setup, execution, and teardown"""

    def __init__(self, ad: android_device.AndroidDevice ,coordinates: Dict[str, :Tuple[int, int]]):
        self.ad = ad
        self.d = u2.connect(ad.serial)
        self.initial_timeout = None

    def setup_test(self) -> bool:
        """Complete test setup: wake device and disable stay awake"""
        logging.info("=" * 60)
        logging.info("Starting Timeout Test Setup")
        logging.info("=" * 60)

        try:
            # Disable 'Stay Awake' from developer settings
            self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")
            self._wake_up_device()
            self.d.press("home")
            time.sleep(2)

            # Verify the device is at home screen
            current_pkg = self.d.info.get("currentPackageName", "")
            asserts.assert_true(
                "launcher" in current_pkg or "home" in current_pkg,
                f"Expected launcher/home, but found: {current_pkg}"
            )

            logging.info("Test setup completed successfully")
            return True

        except Exception as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self):
        super().teardown_test()

    # ---------- Utility Methods ----------
    def _wake_up_device(self) -> None:
        """Wake and unlock the device"""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        time.sleep(1)
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _get_current_timeout(self) -> int:
        """Return current screen timeout in milliseconds"""
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = result.decode('utf-8').strip() if isinstance(result,bytes) else (
                str(result).strip())
            return int(result_str) if result_str.isdigit() else 0
        except Exception as e:
            logging.error("Failed to get current timeout: %s", e)
            return 0

    def _is_screen_off(self) -> bool:
        """Return True if screen is off"""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8")if isinstance(state, bytes) else state
            return "Asleep" in state
        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def _open_timeout_settings(self):
        """Navigate to settings -> Display -> Screen timeout """
        logging.info("Navigate to screen timeout settings...")

        # Launch settings
        self.d.app_start("com.android.settings")
        time.sleep(2)

        # Click Display
        if self.d(text="Display").exists:
            self.d(text="Display").clicks()
            logging.info("Opening Display settings")
        else:
            raise RuntimeError("Could not find 'Display' in settings")

        time.sleep(2)

        # Scroll to and click Screen timeout
        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(textContains="Screen timeout")

        if self.d(textContains="Screen timeout").exists:
            self.d(textContains="Screen timeout").clicks()
            logging.info("Opened screen timeout menu")
        else:
            raise RuntimeError("Could not find 'Screen timeout' option")
        time.sleep(2)



    def _navigate_to_timeout_settings(self) -> None:
        """Navigate to Screen Timeout menu via UI taps"""
        logging.info("Navigating to Screen Timeout settings...")
        nav_steps = [
            ("win_button", "Opening Launcher"),
            ("settings", "Opening Settings"),
            ("display", "Opening Display Settings"),
            ("screen_timeout", "Opening Screen Timeout menu"),
        ]
        for key, msg in nav_steps:
            self._tap_coordinate(key, msg)

    def _go_back_to_home(self) -> None:
        """Return safely to the home screen"""
        logging.info("Returning to home screen...")
        for _ in range(4):
            self.ad.adb.shell("input keyevent KEYCODE_BACK")
            time.sleep(1)
        self.ad.adb.shell("input keyevent KEYCODE_HOME")
        time.sleep(2)

    def test_sequential_timeouts(self, timeout_configs: List[Tuple[str, int, int, str]]) -> None:
        """Sequentially set and verify all timeout options

        Args:
            timeout_configs: List of tuples containing:
                (coordinate_key, expected_ms, wait_time_seconds, description)
        """
        logging.info("Starting sequential timeout tests")

        for key, expected_ms, wait_time, label in timeout_configs:
            logging.info("")
            logging.info("=" * 60)
            logging.info(f"Testing {label} timeout")
            logging.info("=" * 60)

            try:
                # Navigate to timeout settings
                self._navigate_to_timeout_settings()

                # Select the timeout option
                self._tap_coordinate(key, f"Selecting {label} timeout")

                # Verify setting
                current_timeout = self._get_current_timeout()
                logging.info(f"Current timeout value = {current_timeout}ms")

                if current_timeout != expected_ms:
                    logging.error(f"Timeout mismatch for {label}. Expected {expected_ms}, got {current_timeout}")
                    continue

                # Screen-off verification for short durations
                if 0 < wait_time <= 120:
                    logging.info(f"Testing screen timeout behavior ({label})")
                    self._go_back_to_home()
                    self._wake_up_device()

                    logging.info(f"Waiting {wait_time} seconds for screen to turn off...")
                    time.sleep(wait_time)

                    if self._is_screen_off():
                        logging.info(f"Screen turned OFF as expected for {label}.")
                    else:
                        logging.warning(f"Screen still ON after {wait_time} seconds for {label}.")

                    self._wake_up_device()
                else:
                    logging.info(f"Skipping screen-off check for {label}.")
                    self._go_back_to_home()

                logging.info(f"Completed test for {label} timeout.")

            except Exception as e:
                logging.error(f"Error testing {label} timeout: {e}", exc_info=True)


# Factory function
def create_timeout_test(ad, coordinates: Dict[str, Tuple[int, int]]) -> TimeoutTestManager:
    """Factory function to create a TimeoutTestManager instance"""
    return TimeoutTestManager(ad, coordinates)