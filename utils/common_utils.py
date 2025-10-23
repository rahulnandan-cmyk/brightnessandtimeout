#!/usr/bin/env python3
# utils/common_utils.py
import logging
import time
from typing import Tuple, List, Optional, Dict, Any

class DisplayTestManager:
    """Manages display test setup, execution, and teardown"""

    def __init__(self, ad, coordinates: Dict[str, Tuple[int, int]]):
        self.ad = ad
        self.coords = coordinates
        self.initial_brightness = None
        self.final_brightness = None

    def setup_test(self) -> bool:
        """Complete test setup: wake device and navigate to brightness settings"""
        logging.info("=" * 60)
        logging.info("Starting Display Test Setup")
        logging.info("=" * 60)

        try:
            # Wake up device
            self._wake_up_device_simple()

            # Navigate to brightness settings
            self._navigate_to_brightness_settings()

            logging.info("Test setup completed successfully")
            return True

        except Exception as e:
            logging.error("Test setup failed: %s", e)
            return False


    def teardown_test(self) -> None:
        pass

    def _wake_up_device_simple(self) -> bool:
        """Wake up device with basic commands"""
        logging.info("Waking up device...")

        try:
            commands = [
                "input keyevent KEYCODE_WAKEUP",
                "input keyevent KEYCODE_MENU",
                "input keyevent KEYCODE_WAKEUP",
            ]

            for cmd in commands:
                self.ad.adb.shell(cmd)
                time.sleep(1)

            logging.info("Wake-up commands sent successfully")
            return True

        except Exception as e:
            logging.error("Wake-up failed: %s", e)
            return False

    def _navigate_to_brightness_settings(self) -> None:
        """Navigate to brightness settings using coordinates"""
        logging.info("Navigating to brightness settings...")

        steps = [
            ("Opening Launcher", "win_button"),
            ("Clicking Settings", "settings"),
            ("Clicking Display", "display"),
            ("Clicking Brightness", "brightness")
        ]

        for step_name, coord_key in steps:
            logging.info("Step: %s", step_name)
            try:
                x, y = self.coords[coord_key]
                self.ad.adb.shell(f'input tap {x} {y}')
                wait_time = 3 if "Brightness" in step_name else 2
                time.sleep(wait_time)
                logging.debug("%s completed", step_name)
            except Exception as e:
                logging.error("Failed in step '%s': %s", step_name, e)
                raise

        logging.info("Successfully navigated to brightness settings")

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

        logging.error("Failed to retrieve brightness after %d attempts", max_retries)
        return 0

    def _select_brightness_slider(self) -> bool:
        """Properly select the brightness slider for arrow key control"""
        logging.info("Selecting brightness slider for adjustment...")

        try:
            # Method 1: Direct tap on brightness option to open slider dialog
            logging.info("Method 1: Tapping brightness option")
            x, y = self.coords["brightness"]
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2)

        except Exception as e:
            logging.error("Failed to select brightness slider: %s", e)
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



# Factory function
def create_display_test(ad, coordinates: Dict[str, Tuple[int, int]]) -> DisplayTestManager:
    """Factory function to create a DisplayTestManager instance"""
    return DisplayTestManager(ad, coordinates)