#!/usr/bin/env python3
"""Screen Timeout Sequential Test with proper logging"""
import logging
import time
from datetime import datetime

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device


class ScreenTimeoutTest(base_test.BaseTestClass):
    """Sequentially validate screen timeout settings from 15s to 30min."""

    def __init__(self, configs=None):
        super().__init__(configs)
        self.ads = None
        self.ad = None
        self.logger = None
        self.coords = {}

    # ------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------
    def setup_class(self):
        """Initialize device, logging, and coordinates."""
        self.setup_logging()
        self.logger.info("=" * 60)
        self.logger.info("Starting Screen Timeout Sequential Test")
        self.logger.info("=" * 60)

        # Register device
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Exact coordinates on the Android device screen
        self.coords = {
            "win_button": (20, 1055),
            "settings": (296, 577),
            "display": (242, 955),
            "screen_timeout": (56, 520),
            "15_seconds": (83, 252.8),
            "30_seconds": (83, 312),
            "1_minute": (83, 371.2),
            "2_minutes": (83, 430.4),
            "5_minutes": (83, 489.6),
            "10_minutes": (83, 548.8),
            "30_minutes": (83, 616),
        }

        # Disable stay awake
        self.logger.info("Disabling developer 'Stay Awake' option...")
        self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")

    def setup_logging(self):
        """Initialize Python logging to file + console."""
        self.logger = logging.getLogger("ScreenTimeoutTest")
        self.logger.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console logging
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(logging.INFO)

        # File logging
        log_file = f"screen_timeout_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, "w")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
        self.logger.info(f"Logging initialized. Log file: {log_file}")

    # ------------------------------------------------------------
    # Utility functions
    # ------------------------------------------------------------
    def wake_up_device(self):
        """Ensure device is awake."""
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        time.sleep(1)
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def get_current_timeout(self):
        """Return system screen timeout in milliseconds."""
        val = self.ad.adb.shell("settings get system screen_off_timeout").strip()
        return int(val) if val.isdigit() else 0

    def is_screen_off(self):
        """Return True if screen is off."""
        state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
        if isinstance(state, bytes):
            state = state.decode("utf-8", errors="ignore")
        return "Asleep" in state

    def tap_coordinate(self, key, description):
        """Tap a coordinate and log action."""
        self.logger.info(description)
        x, y = self.coords[key]
        self.ad.adb.shell(f"input tap {x} {y}")
        time.sleep(3)

    def navigate_to_timeout_settings(self):
        """Navigate via UI to screen timeout menu."""
        steps = [
            ("win_button", "Opening Launcher"),
            ("settings", "Opening Settings"),
            ("display", "Opening Display settings"),
            ("screen_timeout", "Opening Screen Timeout menu"),
        ]
        for key, msg in steps:
            self.tap_coordinate(key, msg)

    # ------------------------------------------------------------
    # Main Test
    # ------------------------------------------------------------
    def test_sequential_timeouts(self):
        """Run sequential timeout tests from 15s → 30min."""
        timeout_list = [
            ("15_seconds", 15000, 20),
            ("30_seconds", 30000, 35),
            ("1_minute", 60000, 0),
            ("2_minutes", 120000, 0),
            ("5_minutes", 300000, 0),
            ("10_minutes", 600000, 0),
            ("30_minutes", 1800000, 0),
        ]

        for key, expected_ms, wait_sec in timeout_list:
            self._run_single_timeout_test(key, expected_ms, wait_sec)

    def _run_single_timeout_test(self, key, expected_ms, wait_sec):
        """Select timeout, verify value, optionally test screen-off."""
        self.logger.info("=" * 60)
        self.logger.info("Testing timeout: %s", key)
        self.logger.info("=" * 60)

        self.wake_up_device()
        self.navigate_to_timeout_settings()
        self.tap_coordinate(key, f"Selecting {key} timeout")

        # Verify setting
        actual_ms = self.get_current_timeout()
        self.logger.info("Current timeout readback: %sms", actual_ms)
        asserts.assert_equal(actual_ms, expected_ms, f"Timeout mismatch for {key}")

        # Screen-off verification for short durations
        if wait_sec > 0 and wait_sec <= 60:
            self.logger.info("Waiting %d seconds for screen-off check...", wait_sec)
            time.sleep(wait_sec)
            if self.is_screen_off():
                self.logger.info(" Screen turned off as expected for %s", key)
            else:
                self.logger.warning(
                    " Screen still ON after %d seconds for %s", wait_sec, key
                )
            self.wake_up_device()
        else:
            self.logger.info("Skipping screen-off check for long timeout: %s", key)

    # ------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------
    def teardown_class(self):
        """Reset screen timeout to 30 seconds and go home."""
        self.logger.info("Resetting screen timeout to 30 seconds...")
        self.wake_up_device()
        self.navigate_to_timeout_settings()
        self.tap_coordinate("30_seconds", "Selecting 30 seconds timeout")
        self.ad.adb.shell("input keyevent KEYCODE_HOME")
        self.logger.info(" Test completed.")


# ---------------- Main Runner ----------------
if __name__ == "__main__":
    test_runner.main()
