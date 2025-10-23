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
            if not self._wake_up_device():
                return False

            # Navigate to brightness settings
            self._navigate_to_brightness_settings()

            logging.info(" Test setup completed successfully")
            return True

        except Exception as e:
            logging.error("Test setup failed: %s", e)
            return False

    def teardown_test(self) -> None:
        """Complete test teardown"""
        logging.info("=" * 60)
        logging.info("Starting Display Test Teardown")
        logging.info("=" * 60)

        try:
            # Go back to home screen
            self.ad.adb.shell("input keyevent KEYCODE_HOME")
            time.sleep(2)

            # Log final state
            final_brightness = self._get_brightness()
            logging.info("Final device brightness: %d", final_brightness)

            if self.initial_brightness is not None:
                change = final_brightness - self.initial_brightness
                logging.info("Overall brightness change: %d -> %d (=%+d)",
                             self.initial_brightness, final_brightness, change)

            logging.info(" Test teardown completed successfully")

        except Exception as e:
            logging.warning("Teardown had issues: %s", e)

    def _wake_up_device(self, max_retries: int = 3) -> bool:
        """Wake up the device and ensure screen is on"""
        for attempt in range(max_retries):
            try:
                logging.info("Waking up device (attempt %d/%d)...",
                             attempt + 1, max_retries)
                self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
                time.sleep(1)
                self.ad.adb.shell("input keyevent KEYCODE_MENU")
                time.sleep(2)

                # Handle bytes response from ADB
                screen_state_result = self.ad.adb.shell("dumpsys power | grep 'Display Power'")

                # Convert bytes to string if needed
                if isinstance(screen_state_result, bytes):
                    screen_state = screen_state_result.decode('utf-8').strip()
                else:
                    screen_state = str(screen_state_result).strip()

                logging.debug("Screen state: %s", screen_state)

                if "ON" in screen_state.upper():
                    logging.info("Device successfully awakened")
                    return True

            except Exception as e:
                logging.warning("Wake-up attempt %d failed: %s", attempt + 1, e)
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

        logging.error("Failed to wake up device after %d attempts", max_retries)
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
            x, y = self.coords[coord_key]
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2 if "Brightness" in step_name else 3)  # Longer wait for brightness

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

    def execute_brightness_test(self, right_presses: int = 10, left_presses: int = 10,
                                delay: float = 1.0) -> Tuple[int, int, List[tuple]]:
        """Execute complete brightness test with given parameters"""
        logging.info("Starting brightness test: %d RIGHT -> %d LEFT",
                     right_presses, left_presses)

        # Get initial brightness
        self.initial_brightness = self._get_brightness()
        logging.info("Initial brightness: %d", self.initial_brightness)

        brightness_values = []

        # Increase brightness
        logging.info("Phase 1: Increasing brightness (%d RIGHT presses)", right_presses)
        for i in range(right_presses):
            try:
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                brightness_values.append(("RIGHT", i + 1, curr))
                logging.debug("RIGHT %d/%d → Brightness: %d", i + 1, right_presses, curr)
            except Exception as e:
                logging.error("Error during RIGHT press %d: %s", i + 1, e)

        time.sleep(2)
        logging.info("✓ Maximum brightness reached")

        # Decrease brightness
        logging.info("Phase 2: Decreasing brightness (%d LEFT presses)", left_presses)
        for i in range(left_presses):
            try:
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                time.sleep(delay)
                curr = self._get_brightness()
                brightness_values.append(("LEFT", i + 1, curr))
                logging.debug("LEFT %d/%d → Brightness: %d", i + 1, left_presses, curr)
            except Exception as e:
                logging.error("Error during LEFT press %d: %s", i + 1, e)

        # Confirm selection
        self.ad.adb.shell("input keyevent KEYCODE_ENTER")
        time.sleep(3)

        # Get final brightness
        self.final_brightness = self._get_brightness()

        # Log summary
        change = self.final_brightness - self.initial_brightness
        logging.info("Brightness test completed: %d → %d (Δ=%+d)",
                     self.initial_brightness, self.final_brightness, change)

        return self.initial_brightness, self.final_brightness, brightness_values


# Standalone functions for backward compatibility
def create_display_test(ad, coordinates: Dict[str, Tuple[int, int]]) -> DisplayTestManager:
    """Factory function to create a DisplayTestManager instance"""
    return DisplayTestManager(ad, coordinates)
