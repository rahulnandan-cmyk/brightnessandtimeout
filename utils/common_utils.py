#!/usr/bin/env python3
# utils/common_utils.py
import logging
import time
from typing import Tuple, List, Optional

def wake_up_device(ad, max_retries: int = 3) -> str:
    """Wake up the device and ensure screen is on."""
    for attempt in range(max_retries):
        try:
            logging.info("Waking up device (attempt %d/%d)...", attempt + 1, max_retries)
            ad.adb.shell("input keyevent KEYCODE_WAKEUP")
            time.sleep(1)
            ad.adb.shell("input keyevent KEYCODE_MENU")
            time.sleep(2)

            # Handle bytes response from ADB
            screen_state_result = ad.adb.shell("dumpsys power | grep 'Display Power'")

            # Convert bytes to string if needed
            if isinstance(screen_state_result, bytes):
                screen_state = screen_state_result.decode('utf-8').strip()
            else:
                screen_state = str(screen_state_result).strip()

            logging.debug("Screen state: %s", screen_state)

            if "ON" in screen_state.upper():
                logging.info("Device successfully awakened")
                return screen_state

        except Exception as e:
            logging.warning("Wake-up attempt %d failed: %s", attempt + 1, e)
            if attempt == max_retries - 1:
                raise
            time.sleep(2)

    return "Unknown"


def get_brightness(ad, max_retries: int = 3) -> int:
    """Get current brightness with retry logic and better error handling."""
    for attempt in range(max_retries):
        try:
            result = ad.adb.shell("settings get system screen_brightness")

            # Handle bytes response from ADB
            if isinstance(result, bytes):
                result_str = result.decode('utf-8').strip()
            else:
                result_str = str(result).strip()

            logging.debug("Raw brightness result: %s", result_str)

            # Handle different response formats
            if not result_str or result_str == "null":
                logging.warning("Empty brightness value (attempt %d)", attempt + 1)
                continue

            if result_str.isdigit():
                brightness = int(result_str)
                logging.debug("Brightness retrieved: %d", brightness)
                return brightness
            else:
                logging.warning("Non-digit brightness value: %s (attempt %d)", result_str, attempt + 1)

        except Exception as e:
            logging.error("Failed to get brightness (attempt %d): %s", attempt + 1, e)
            if attempt == max_retries - 1:
                raise

        time.sleep(1)

    logging.error("Failed to retrieve brightness after %d attempts", max_retries)
    return 0


def adjust_brightness(ad, right_presses: int = 10, left_presses: int = 10,
                      delay: float = 1.0) -> Tuple[int, int, List[tuple]]:
    """Adjust brightness using arrow keys (RIGHT → LEFT pattern)."""
    logging.info("Starting brightness adjustment: %d RIGHT -> %d LEFT",
                 right_presses, left_presses)

    # Get initial brightness
    initial_brightness = get_brightness(ad)
    logging.info("Initial brightness: %d", initial_brightness)

    brightness_values = []

    # Increase brightness
    logging.info("Increasing brightness...")
    for i in range(right_presses):
        try:
            ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
            time.sleep(delay)
            curr = get_brightness(ad)
            brightness_values.append(("RIGHT", i + 1, curr))
            logging.debug("RIGHT %d/%d -> Brightness: %d", i + 1, right_presses, curr)
        except Exception as e:
            logging.error("Error during RIGHT press %d: %s", i + 1, e)

    time.sleep(2)
    logging.info("Maximum brightness reached, pausing...")

    # Decrease brightness
    logging.info("Decreasing brightness...")
    for i in range(left_presses):
        try:
            ad.adb.shell("input keyevent KEYCODE_DPAD_LEFT")
            time.sleep(delay)
            curr = get_brightness(ad)
            brightness_values.append(("LEFT", i + 1, curr))
            logging.debug("LEFT %d/%d -> Brightness: %d", i + 1, left_presses, curr)
        except Exception as e:
            logging.error("Error during LEFT press %d: %s", i + 1, e)

    # Confirm selection
    ad.adb.shell("input keyevent KEYCODE_ENTER")
    time.sleep(3)

    # Get final brightness
    final_brightness = get_brightness(ad)

    # Log summary
    change = final_brightness - initial_brightness
    logging.info("Brightness change summary: %d → %d (Δ=%+d)",
                 initial_brightness, final_brightness, change)

    return initial_brightness, final_brightness, brightness_values