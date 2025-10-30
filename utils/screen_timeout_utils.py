#!/usr/bin/env python3
# utils/screen_timeout_utils.py

import logging
import time
import uiautomator2 as u2
from typing import Tuple, List, Dict, Any
from mobly import asserts
from mobly.controllers import android_device


class TimeoutTestManager:
    """Manages screen timeout test setup, execution, and teardown using UIAutomator2."""

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d = u2.connect(ad.serial)
        self.initial_timeout = None

    def setup_test(self) -> bool:
        """Prepare device: wake up, disable stay-awake, and verify launcher."""
        logging.info("=" * 60)
        logging.info("Starting Timeout Test Setup")
        logging.info("=" * 60)

        try:
            self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")
            self._wake_up_device()
            self._ensure_home_screen()
            time.sleep(2)

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

    def teardown_test(self, default_timeout_ms: int = 30000) -> None:
        """Reset screen timeout to default and return home."""
        try:
            logging.info("Resetting screen timeout to default (30s)...")
            self._wake_up_device()
            self._ensure_home_screen()

            # Use ADB to directly set timeout to 30 seconds
            # Try selecting "30 seconds"
            if self.d(text="30 seconds").exists:
                self.d(text="30 seconds").click()
                time.sleep(2)

            # Verify reset
            current_timeout = self._get_current_timeout()
            if current_timeout == default_timeout_ms:
                logging.info("Timeout reset to 30 seconds successfully")
            else:
                logging.warning(f"Timeout reset mismatch: got {current_timeout}ms")

            self.d.press("home")
            time.sleep(2)

        except Exception as e:
            logging.error("Teardown failed: %s", e, exc_info=True)

    def _wake_up_device(self):
        """Wake device and dismiss lockscreen."""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _get_current_timeout(self) -> int:
        """Get current screen timeout (ms)."""
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = result.decode('utf-8').strip() \
                if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else 0
        except Exception as e:
            logging.error("Failed to get timeout: %s", e)
            return 0

    def _is_screen_off(self) -> bool:
        """Check if screen is off."""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state
        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def _open_timeout_settings(self):
        """Navigate to Settings -> Display -> Screen timeout."""
        logging.info("Navigating to Screen Timeout settings...")

        # Launch Settings
        self.d.app_start("com.android.settings")
        time.sleep(2)

        # Click "Display"
        if self.d(text="Display").exists:
            self.d(text="Display").click()
            logging.info("Opened Display settings")
        else:
            raise RuntimeError("Could not find 'Display' in Settings")

        time.sleep(2)

        # Scroll to and click "Screen timeout"
        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(textContains="Screen timeout")

        if self.d(textContains="Screen timeout").exists:
            self.d(textContains="Screen timeout").click()
            logging.info("Opened Screen timeout menu")
        else:
            raise RuntimeError("Could not find 'Screen timeout' option")

        time.sleep(2)

    def test_sequential_timeouts(self, timeout_labels: List[Tuple[str, int, int]]):
        """
        Sequentially test timeout options via UIAutomator2.

        Args:
            timeout_labels: List of tuples (timeout_text, expected_ms, wait_sec)
                e.g. [("15 seconds", 15000, 20), ("30 seconds", 30000, 40)]
        """
        for label, expected_ms, wait_sec in timeout_labels:
            logging.info("=" * 60)
            logging.info(f"Testing timeout option: {label}")
            logging.info("=" * 60)

            try:
                self._open_timeout_settings()

                # Select timeout text (like "15 seconds")
                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info(f"Selected timeout: {label}")
                else:
                    logging.warning(f"Timeout option '{label}' not found")
                    continue

                time.sleep(2)

                # Verify the value
                current_timeout = self._get_current_timeout()
                if current_timeout != expected_ms:
                    logging.error(f"Timeout mismatch! Expected {expected_ms}, got {current_timeout}")
                else:
                    logging.info(f"Timeout set correctly to {expected_ms} ms")

                # screen-off test
                if wait_sec > 0:
                    logging.info(f"Waiting {wait_sec}s for screen-off verification...")
                    time.sleep(wait_sec)
                    if self._is_screen_off():
                        logging.info(f"Screen turned off as expected ({label})")
                        self._wake_up_device()
                    else:
                        logging.warning(f"Screen still ON after {wait_sec}s ({label})")

                self.d.press("home")

            except Exception as e:
                logging.error(f"Error testing timeout '{label}': {e}", exc_info=True)


def create_timeout_test(ad: android_device.AndroidDevice,
                        coords: Dict[str, Tuple[int, int]] = None) -> TimeoutTestManager:
    """Factory function to create a TimeoutTestManager instance.

    Args:
        ad: Android device instance
        coords: Dictionary of UI coordinates (unused in current implementation)

    Returns:
        TimeoutTestManager instance
    """
    return TimeoutTestManager(ad)