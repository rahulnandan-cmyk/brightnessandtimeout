#!/usr/bin/env python3
"""Brightness API functions."""
import logging
import time
from typing import Tuple

from utils.display_settings_manager1 import DisplaySettingsManager


class BrightnessAPI:
    """API for brightness-related test operations."""

    def __init__(self, manager: DisplaySettingsManager):
        self.manager = manager
        # Alias key manager functions for cleaner access
        self.ad = self.manager.ad

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
            # Navigate to brightness settings
            self.manager.navigate_to_brightness_settings()

            initial_brightness = self.manager.get_brightness()
            logging.info("Initial brightness: %d", initial_brightness)

            # 1. Increasing brightness.
            logging.info("Increasing brightness (%d steps)", right_press)
            for i in range(right_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self.manager.get_brightness()
                logging.info("Right %d/%d -> Brightness: %d", i + 1, right_press, curr)

            # 2. Decreasing Brightness
            logging.info("Decreasing brightness (%d steps)", left_press)
            for i in range(left_press):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
                time.sleep(delay)
                curr = self.manager.get_brightness()
                logging.info("Left %d/%d -> Brightness: %d", i + 1, left_press, curr)

            final_brightness = self.manager.get_brightness()
            logging.info("Final Brightness: %d", final_brightness)

            self.manager.close_settings_dialogs()  # clean up the UI

            # Returns two values: initial and final brightness for assertion
            return initial_brightness, final_brightness
        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Error during brightness test: %s", e, exc_info=True)
            self.manager.close_settings_dialogs()  # Ensure cleanup even on failure
            raise

    def verify_brightness_range(self, min_brightness: int = 0, max_brightness: int = 255) -> bool:
        """
        Verifies that the current brightness is within the expected range.

        :param min_brightness: Minimum acceptable brightness value
        :param max_brightness: Maximum acceptable brightness value
        :returns: True if brightness is within range, False otherwise
        :rtype: bool
        """
        try:
            current_brightness = self.manager.get_brightness()
            if min_brightness <= current_brightness <= max_brightness:
                logging.info("Brightness %d is within expected range [%d, %d]",
                             current_brightness, min_brightness, max_brightness)
                return True

            logging.warning("Brightness %d is outside expected range [%d, %d]",
                            current_brightness, min_brightness, max_brightness)
            return False
        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Error verifying brightness range: %s", e)
            return False
