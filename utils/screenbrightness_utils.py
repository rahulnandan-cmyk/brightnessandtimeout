#!/usr/bin/env python3
# utils/screenbrightness_utils.py
import logging
import time
import uiautomator2 as u2
from typing import Tuple, List, Optional, Dict, Any

from  mobly.controllers import  android_device

class DisplayTestManager:
    """Manages display test setup, execution, and teardown"""
    
    # Keywords for robust navigation in settings
    DISPLAY_LABELS = [
        "Display", "Screen", "Screen & display", "Display & brightness", "Display settings"
    ]
    
    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d = u2.connect(ad.serial)
        self.initial_brightness = None
        self.final_brightness = None

    def setup_test(self) -> bool:
        """Complete test setup: wake device and navigate to display settings"""
        logging.info("=" * 60)
        logging.info("Starting Display Test Setup")
        logging.info("=" * 60)

        try:
            # Wake up device
            self._wake_up_device_simple()
            self._enusre_home_screen()
            logging.info("Test setup completed successfully")
            return True
        except Exception as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self) -> None:
        """Go back to home screen and ensure cleanup"""
        try:
            logging.info("Starting teardown - closing dialogs and returning to home")
            self.ad.adb.shell("input keyevent KEYCODE_HOME")
            self.d.press("home")
            time.sleep(2)
        except Exception as e:
            logging.warning("Home command failed: %s", e)

    def _ensure_home_screen(self):
        """Ensure the device is on the home screen."""
        pass

    def _wake_up_device(self) -> None:
        """Wake up device with basic commands"""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)


    def _navigate_to_display_settings(self) -> None:
        """Navigate to display settings using coordinates"""
        logging.info("Navigating to display settings...")

        steps = [
            ("Opening Launcher", "win_button"),
            ("Clicking Settings", "settings"),
            ("Clicking Display", "display"),
        ]

        for step_name, coord_key in steps:
            logging.info("Step: %s", step_name)
            try:
                x, y = self.coords[coord_key]
                self.ad.adb.shell(f'input tap {x} {y}')
                wait_time = 2
                time.sleep(wait_time)
                logging.debug("%s completed", step_name)
            except Exception as e:
                logging.error("Failed in step '%s': %s", step_name, e)
                raise

        logging.info("Successfully navigated to display settings")

    def _navigate_to_brightness_settings(self) -> None:
        """Navigate to brightness settings from display settings"""
        logging.info("Navigating to brightness settings...")
        try:
            x, y = self.coords["brightness"]
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(3)
            logging.info("Successfully navigated to brightness settings")
        except Exception as e:
            logging.error("Failed to navigate to brightness: %s", e)
            raise

    def _navigate_to_timeout_settings(self) -> None:
        """Navigate to screen timeout settings from display settings"""
        logging.info("Navigating to screen timeout settings...")
        try:
            x, y = self.coords["screen_timeout"]
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(3)
            logging.info("Successfully navigated to screen timeout settings")
        except Exception as e:
            logging.error("Failed to navigate to screen timeout: %s", e)
            raise

    def _get_brightness(self, max_retries: int = 3) -> int:
        """Get current brightness with retry logic"""
        for attempt in range(max_retries):
            try:
                result = self.ad.adb.shell("settings get system screen_brightness")

                # Handle bytes response from ADB
                if isinstance(result, bytes):
                    result_str = result.decode('utf-8').strip()
                else:
                    result_str = str(result).strip()

                logging.debug("Raw brightness result: %s", result_str)

                if not result_str or result_str == "null":
                    logging.warning("Empty brightness value (attempt %d)", attempt + 1)
                    continue

                if result_str.isdigit():
                    return int(result_str)
                else:
                    logging.warning("Non-digit brightness value: %s (attempt %d)",
                                    result_str, attempt + 1)

            except Exception as e:
                logging.error("Failed to get brightness (attempt %d): %s",
                              attempt + 1, e)
                if attempt == max_retries - 1:
                    raise

            time.sleep(1)

        logging.error("Failed to retrieve brightness after %d attempts",
                      max_retries)
        return 0

    def _get_timeout(self, max_retries: int = 3) -> int:
        """Get current screen timeout with retry logic"""
        for attempt in range(max_retries):
            try:
                result = self.ad.adb.shell("settings get system screen_off_timeout")

                # Handle bytes response from ADB
                if isinstance(result, bytes):
                    result_str = result.decode('utf-8').strip()
                else:
                    result_str = str(result).strip()

                logging.debug("Raw timeout result: %s", result_str)

                if not result_str or result_str == "null":
                    logging.warning("Empty timeout value (attempt %d)", attempt + 1)
                    continue

                if result_str.isdigit():
                    return int(result_str)
                else:
                    logging.warning("Non-digit timeout value: %s (attempt %d)",
                                    result_str, attempt + 1)

            except Exception as e:
                logging.error("Failed to get timeout (attempt %d): %s",
                              attempt + 1, e)
                if attempt == max_retries - 1:
                    raise

            time.sleep(1)

        logging.error("Failed to retrieve timeout after %d attempts", max_retries)
        return 0

    def _is_screen_off(self) -> bool:
        """Return True if screen is off."""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            if isinstance(state, bytes):
                state = state.decode("utf-8", errors="ignore")
            return "Asleep" in state
        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def _adjust_brightness_with_retry(self, right_presses: int, left_presses: int, delay: float) \
            -> Tuple[int, int, List[tuple]]:
        """Try different methods to adjust brightness"""
        brightness_values = []

        # Get initial brightness
        initial = self._get_brightness()
        logging.info("Initial brightness before adjustment: %d", initial)

        # Method 1: Standard arrow key adjustment
        logging.info("Attempting Method 1: Arrow key adjustment")
        current_method_brightness = initial

        for i in range(right_presses):
            try:
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                brightness_values.append(("RIGHT", i + 1, curr))
                logging.info("RIGHT %d/%d -> Brightness: %d", i + 1, right_presses, curr)
                current_method_brightness = curr
            except Exception as e:
                logging.error("Error during RIGHT press %d: %s", i + 1, e)

        # Check if Method 1 worked
        if current_method_brightness != initial:
            for i in range(left_presses):
                try:
                    self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                    time.sleep(delay)
                    curr = self._get_brightness()
                    brightness_values.append(("LEFT", i + 1, curr))
                    logging.info("LEFT %d/%d → Brightness: %d", i + 1, left_presses, curr)
                except Exception as e:
                    logging.error("Error during LEFT press %d: %s", i + 1, e)

        return initial, self._get_brightness(), brightness_values

    def execute_brightness_test(self, right_presses: int = 10, left_presses: int = 10,
                                delay: float = 1.0) -> Tuple[int, int, List[tuple]]:
        """Execute complete brightness test with given parameters"""
        logging.info("Starting brightness test: %d RIGHT -> %d LEFT",
                     right_presses, left_presses)

        # Navigate to brightness settings
        self._navigate_to_brightness_settings()

        # Get initial brightness
        self.initial_brightness = self._get_brightness()
        logging.info("Initial brightness: %d", self.initial_brightness)

        # Select brightness slider properly
        if not self._select_brightness_slider():
            logging.warning("Could not select brightness slider, trying direct adjustment")

        # Adjust brightness with retry logic
        initial, final, brightness_values = self._adjust_brightness_with_retry(
            right_presses, left_presses, delay
        )

        time.sleep(2)

        # Get final brightness
        self.final_brightness = self._get_brightness()

        # Log summary
        change = self.final_brightness - self.initial_brightness
        logging.info("Brightness test completed: %d → %d (=%+d)",
                     self.initial_brightness, self.final_brightness, change)

        return self.initial_brightness, self.final_brightness, brightness_values

    def test_brightness_adjustment(self, right_presses: int = 10, left_presses: int = 10,
                                   delay: float = 1.0):
        """Sequentially adjusts brightness up and down using uiautomator"""
    logging.info("=" * 60)
    logging.info("Starting  Brightness Test")
    logging.info("=" * 60)




# Factory function
def create_display_test(ad, coordinates: Dict[str, Tuple[int, int]]) -> DisplayTestManager:
    """Factory function to create a DisplayTestManager instance"""
    return DisplayTestManager(ad, coordinates)
