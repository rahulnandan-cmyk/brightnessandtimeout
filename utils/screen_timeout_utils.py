#!/usr/bin/env python3
"""
Utility: Screen Timeout Test Manager
Manages screen timeout setup, validation, and teardown using UIAutomator2.
"""

import logging
import time
import uiautomator2 as u2
from typing import Dict, Tuple, Any


class TimeoutTestManager:
    """Manages screen timeout test setup, execution, and teardown."""

    def __init__(self, serial: str, coordinates: Dict[str, Tuple[int, int]]):
        """
        Initialize TimeoutTestManager.

        Args:
            serial (str): Device serial number for ADB/UIAutomator2 connection.
            coordinates (dict): Dictionary of UI element coordinates (e.g., for tapping).
        """
        self.serial = serial
        self.coords = coordinates
        self.device = None
        self.initial_timeout = None

    # ------------------------------------------------------
    # SETUP PHASE
    # ------------------------------------------------------
    def setup_test(self) -> None:
        """Establish connection and record the current timeout value."""
        logging.info("🔌 Connecting to device via UIAutomator2...")
        self.device = u2.connect(self.serial)
        logging.info(f"Connected to {self.serial}: {self.device.info}")

        # Read current timeout setting
        self.initial_timeout = self.device.shell("settings get system screen_off_timeout").strip()
        logging.info(f"Initial screen timeout: {self.initial_timeout} ms")

    # ------------------------------------------------------
    # ACTION PHASE
    # ------------------------------------------------------
    def select_timeout_option(self, timeout_label: str) -> None:
        """
        Navigate UI and select a screen timeout option.

        Args:
            timeout_label (str): Text label of the timeout option, e.g., "30 seconds"
        """
        logging.info(f"Opening Display → Screen Timeout → Selecting {timeout_label}")

        # Launch Display settings
        self.device.shell("am start -a android.settings.DISPLAY_SETTINGS")
        time.sleep(2)

        # Scroll and click the "Screen timeout" option
        if self.device(textContains="Screen timeout").exists(timeout=5):
            self.device(textContains="Screen timeout").click()
            time.sleep(1)
        else:
            logging.warning("⚠️ 'Screen timeout' option not found in Display Settings.")
            return

        # Select the timeout option
        if self.device(textContains=timeout_label).exists(timeout=3):
            self.device(textContains=timeout_label).click()
            logging.info(f"✅ Selected timeout: {timeout_label}")
        else:
            logging.warning(f"⚠️ Timeout option '{timeout_label}' not found.")

    # ------------------------------------------------------
    # VALIDATION PHASE
    # ------------------------------------------------------
    def verify_timeout(self, expected_ms: int) -> bool:
        """Verify if the current timeout matches the expected value."""
        current_value = self.device.shell("settings get system screen_off_timeout").strip()
        logging.info(f"📋 Current timeout setting: {current_value} ms (Expected: {expected_ms} ms)")

        if current_value == str(expected_ms):
            logging.info("✅ Timeout value verified successfully.")
            return True
        else:
            logging.error("❌ Timeout value mismatch.")
            return False

    # ------------------------------------------------------
    # TEARDOWN PHASE
    # ------------------------------------------------------
    def teardown_test(self) -> None:
        """Restore the original screen timeout setting."""
        if self.initial_timeout:
            logging.info(f"Restoring original timeout: {self.initial_timeout}")
            self.device.shell(f"settings put system screen_off_timeout {self.initial_timeout}")
        else:
            logging.warning("⚠️ No initial timeout value recorded.")
        logging.info("🧹 Test teardown completed.")


# ------------------------------------------------------
# Factory Helper
# ------------------------------------------------------
def create_timeout_test(serial: str, coords: Dict[str, Tuple[int, int]]) -> TimeoutTestManager:
    """
    Factory function to create TimeoutTestManager instance.

    Args:
        serial (str): Device serial number
        coords (dict): Coordinate map
    """
    return TimeoutTestManager(serial, coords)
