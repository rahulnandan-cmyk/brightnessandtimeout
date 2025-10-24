#!/usr/bin/env python3
# utils/screen_timeout_utils.py
import logging
import time
from typing import Tuple, List, Dict, Any, Optional

class TimeoutTestManager:
    """Manages screen timeout test setup, execution, and teardown"""

    def __init__(self, ad, coordinates: Dict[str, Tuple[int, int]]):
        self.ad = ad
        self.coords = coordinates
        self.initial_timeout = None

    def setup_test(self) -> bool:
        """Complete test setup: wake device and disable stay awake"""
        logging.info("=" * 60)
        logging.info("Starting Timeout Test Setup")
        logging.info("=" * 60)

        try:
            # Disable 'Stay Awake' from developer settings
            self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")

            # Wake up device
            self._wake_up_device()

            # Navigate to home screen
            self.ad.adb.shell("input keyevent KEYCODE_HOME")
            time.sleep(2)

            logging.info("Test setup completed successfully")
            return True

        except Exception as e:
            logging.error("Test setup failed: %s", e)
            return False

    def teardown_test(self, default_timeout_key: str = "30_seconds") -> None:
        """Reset screen timeout to default and return to home screen"""
        try:
            logging.info("Resetting screen timeout to default")

            # Wake up device
            self._wake_up_device()

            # Navigate to timeout settings
            self._navigate_to_timeout_settings()

            # Select default timeout
            x, y = self.coords[default_timeout_key]
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2)

            # Verify reset
            current_timeout = self._get_current_timeout()
            if current_timeout == 30000:  # 30 seconds in ms
                logging.info("Timeout reset to 30 seconds successfully")
            else:
                logging.warning(f"Timeout reset mismatch: {current_timeout}ms")

            # Return to home
            self._go_back_to_home()

        except Exception as e:
            logging.error("Teardown failed: %s", e)

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
            timeout = self.ad.adb.shell("settings get system screen_off_timeout")

            # Handle bytes response from ADB
            if isinstance(timeout, bytes):
                timeout_str = timeout.decode('utf-8').strip()
            else:
                timeout_str = str(timeout).strip()

            return int(timeout_str) if timeout_str.isdigit() else 0
        except Exception as e:
            logging.error("Failed to get current timeout: %s", e)
            return 0

    def _is_screen_off(self) -> bool:
        """Return True if screen is off"""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            if isinstance(state, bytes):
                state = state.decode("utf-8", errors="ignore")
            return "Asleep" in state
        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def _tap_coordinate(self, key: str, description: str) -> None:
        """Tap on the specified coordinate"""
        logging.info(description)
        x, y = self.coords[key]
        self.ad.adb.shell(f"input tap {x} {y}")
        time.sleep(3)

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