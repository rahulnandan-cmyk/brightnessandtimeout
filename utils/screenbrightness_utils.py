# utils/screenbrightness_utils.py
"""Utility class for coordinate-free screen brightness testing using Mobly and UIAutomator2."""

import logging
import time
import uiautomator2 as u2
from typing import Tuple, List, Dict
from mobly import asserts
from mobly.controllers import android_device

class BrightnessTestManager:
    """Manages screen brightness test setup, execution, and teardown using UIAutomator2."""

    HOME_KEYWORDS = ["launcher", "home"]
    DISPLAY_LABELS = [
        "Display", "Screen", "Screen & display", "Display & brightness", "Display settings"
    ]

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d = u2.connect(ad.serial)

    def setup_test(self) -> bool:
        """Complete test setup: wake device and ensure home screen."""
        logging.info("=" * 60)
        logging.info("Starting Brightness Test Setup")
        logging.info("=" * 60)
        try:
            self._wake_up_device()
            self._ensure_home_screen()
            logging.info("Test setup completed successfully")
            return True
        except Exception as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self) -> None:
        """Go back to home screen and ensure cleanup."""
        try:
            logging.info("Starting teardown - closing dialogs and returning to home...")
            # Use three back presses to dismiss dialogs
            for _ in range(3):
                self.d.press("back")
                time.sleep(0.5)
            self.d.press("home")
            time.sleep(1)
        except Exception as e:
            logging.warning("Teardown failed: %s", e)

    def _ensure_home_screen(self):
        """Ensures the device is on the home screen."""
        logging.info("Ensuring Home screen...")
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                return
        raise RuntimeError("Home screen not detected. Package: %s" % pkg)

    def _wake_up_device(self):
        """Wakes up device and dismisses keyguard."""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _get_brightness(self) -> int:
        """Get current brightness using ADB shell (coordinate-free)."""
        try:
            result = self.ad.adb.shell("settings get system screen_brightness")
            result_str = result.decode('utf-8').strip() \
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else -1
        except Exception as e:
            logging.error("Failed to get brightness: %s", e)
            return -1

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
            # Scrolling logic to find Display menu
            for _ in range(5):
                self.d(scrollable=True).scroll(steps=10)
                for label in self.DISPLAY_LABELS:
                    if self.d(text=label).exists:
                        self.d(text=label).click()
                        logging.info(f"Opened '{label}' settings after scrolling")
                        found_display = True
                        break
                if found_display:
                    break

        if not found_display:
            raise RuntimeError("Could not find 'Display' in Settings")

        time.sleep(2)

    def _navigate_to_brightness_settings(self):
        """Navigates to brightness settings from the Display menu (coordinate-free)."""
        logging.info("Navigating to brightness settings...")

        # 1. Ensure we are at the Display settings menu
        self._navigate_to_display_menu()

        # 2. Scroll to and click the brightness option
        brightness_labels = ["Brightness level", "Adaptive brightness", "Brightness"]
        found_brightness = False

        for label in brightness_labels:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info(f"Clicked brightness option: '{label}'")
                found_brightness = True
                break

        if not found_brightness:
            # Fallback: Scroll and search for partial text
            if self.d(scrollable=True).exists:
                self.d(scrollable=True).scroll.to(textContains="Brightness")

            if self.d(textContains="Brightness").exists:
                self.d(textContains="Brightness").click()
                logging.info("Clicked 'Brightness' after scrolling")
            else:
                raise RuntimeError("Could not find any 'Brightness' option in Settings.")

        time.sleep(2)

    def test_brightness_adjustment(self, right_presses: int = 10, left_presses: int = 10,
                                   delay: float = 1.0):
        """Sequentially adjusts brightness up and down using coordinate-free DPAD keys."""

        logging.info("=" * 60)
        logging.info(f"Starting Brightness Adjustment Test")
        logging.info("=" * 60)

        try:
            self._navigate_to_brightness_settings()

            initial_brightness = self._get_brightness()
            logging.info(f"Initial brightness: {initial_brightness}")

            # Adjustment UP (DPAD_RIGHT) - Coordinate-free key press
            logging.info(f"Adjusting UP ({right_presses} steps)")
            for i in range(right_presses):
                self.ad.adb.shell("input keyevent KEYCODE_DPAD_RIGHT")
                time.sleep(delay)
                curr = self._get_brightness()
                logging.info(f"UP {i+1}/{right_presses} -> Brightness: {curr}")

            # Adjustment DOWN (DPAD_LEFT) - Coordinate-free key press
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

            return initial_brightness, final_brightness

        except Exception as e:
            logging.error(f"Error during brightness test: {e}", exc_info=True)
            self.d.press("home")
            time.sleep(1)

            raise

# Factory function for Mobly
def create_brightness_test(ad: android_device.AndroidDevice) -> BrightnessTestManager:
    """Factory function to create a BrightnessTestManager instance."""
    return BrightnessTestManager(ad)