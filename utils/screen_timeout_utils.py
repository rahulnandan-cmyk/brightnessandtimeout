import logging
import time
import uiautomator2 as u2
from typing import Tuple, List, Dict
from mobly import asserts
from mobly.controllers import android_device

class TimeoutTestManager:
    """Manages screen timeout test setup, execution, and teardown using UIAutomator2."""

    HOME_KEYWORDS = ["launcher", "home"]

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d = u2.connect(ad.serial)

    def setup_test(self) -> bool:
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
                any(keyword in current_pkg.lower() for keyword in self.HOME_KEYWORDS),
                f"Expected home/launcher, but found: {current_pkg}"
            )
            logging.info("Test setup completed successfully")
            return True
        except Exception as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self, default_timeout_ms: int = 30000) -> None:
        try:
            logging.info("Starting teardown - closing dialogs and returning to home...")
            # First, close any open dialogs with back button
            for _ in range(3):
                self.d.press("back")
                time.sleep(0.5)

            # Now try to return to home screen
            for attempt in range(5):
                self.d.press("home")
                time.sleep(1)
                pkg = self.d.info.get("currentPackageName", "")
                if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                    logging.info(f"Home screen detected: {pkg}")
                    break
                else:
                    logging.warning(f"Home screen not detected yet, attempt {attempt+1}: current pkg {pkg}")
            else:
                logging.warning("Could not confirm home screen, forcing app stop")
                self.ad.adb.shell("am force-stop com.android.settings")
                time.sleep(1)
                self.d.press("home")
                time.sleep(1)

            # Reset timeout to 30 seconds via settings command
            logging.info("Resetting timeout to 30 seconds...")
            self.ad.adb.shell("settings put system screen_off_timeout 30000")
            time.sleep(1)

            current_timeout = self._get_current_timeout()
            if current_timeout == default_timeout_ms:
                logging.info("Timeout reset to 30 seconds successfully")
            else:
                logging.warning(f"Timeout reset mismatch: got {current_timeout}ms, expected {default_timeout_ms}ms")

        except Exception as e:
            logging.error("Teardown failed: %s", e, exc_info=True)

    def _ensure_home_screen(self):
        logging.info("Ensuring Home screen...")
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            logging.info(f"Current package: {pkg}")
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                logging.info(f"Home screen detected: {pkg}")
                return
        raise RuntimeError("Home screen not detected. Package: %s" % pkg)

    def _wake_up_device(self):
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def _get_current_timeout(self) -> int:
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = result.decode('utf-8').strip() if isinstance(result, bytes) else str(result).strip()
            return int(result_str) if result_str.isdigit() else 0
        except Exception as e:
            logging.error("Failed to get timeout: %s", e)
            return 0

    def _is_screen_off(self) -> bool:
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state
        except Exception as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def _close_settings_dialogs(self):
        """Close any open settings dialogs and return to home."""
        logging.info("Closing any open settings dialogs...")
        # Press back multiple times to exit any dialogs/settings
        for _ in range(3):
            self.d.press("back")
            time.sleep(0.5)
        # Return to home
        self.d.press("home")
        time.sleep(1)

    def _open_timeout_settings(self):
        logging.info("Navigating to Screen Timeout settings...")

        # First, ensure we're starting fresh - close any open dialogs
        self._close_settings_dialogs()

        # Now open settings app from home
        self.d.app_start("com.android.settings")
        time.sleep(3)

        # Check if we accidentally landed on the timeout dialog
        if self.d(text="15 seconds").exists and self.d(text="30 seconds").exists:
            logging.warning("Landed on timeout dialog directly, going back to main settings")
            self.d.press("back")
            time.sleep(2)

        display_labels = [
            "Display", "Screen", "Screen & display", "Display & brightness", "Display settings"
        ]
        found_display = False

        for label in display_labels:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info(f"Opened '{label}' settings")
                found_display = True
                break

        if not found_display:
            for _ in range(5):
                self.d(scrollable=True).scroll(steps=10)
                for label in display_labels:
                    if self.d(text=label).exists:
                        self.d(text=label).click()
                        logging.info(f"Opened '{label}' settings after scrolling")
                        found_display = True
                        break
                if found_display:
                    break

        if not found_display:
            options = [el.text for el in self.d.xpath('//*[@text]').all()]
            logging.error(f"Could not find Display section! Available Settings options: {options}")
            raise RuntimeError("Could not find 'Display' in Settings")

        time.sleep(2)

        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(textContains="Screen timeout")

        if self.d(textContains="Screen timeout").exists:
            self.d(textContains="Screen timeout").click()
            logging.info("Opened 'Screen timeout' menu")
        else:
            options = [el.text for el in self.d.xpath('//*[@text]').all()]
            logging.error(f"'Screen timeout' menu not found! Options: {options}")
            raise RuntimeError("Could not find 'Screen timeout' option")

        time.sleep(2)

    def test_sequential_timeouts(self, timeout_labels: List[Tuple[str, int, int, bool]]):
        """
        Test sequential timeout options.

        Args:
            timeout_labels: List of tuples (label, expected_ms, wait_sec, skip)
                - label: UI text to click (e.g., "15 seconds")
                - expected_ms: Expected timeout value in milliseconds
                - wait_sec: Seconds to wait for screen-off verification (0 to skip)
                - skip: If True, skip this test with a message
        """
        for item in timeout_labels:
            # Support both 3-tuple (old format) and 4-tuple (new format with skip)
            if len(item) == 4:
                label, expected_ms, wait_sec, skip = item
            else:
                label, expected_ms, wait_sec = item
                skip = False

            logging.info("=" * 60)
            logging.info(f"Testing timeout option: {label}")
            logging.info("=" * 60)

            if skip:
                logging.info(f"SKIPPED: {label} - Skipping as per test configuration")
                continue

            try:
                self._open_timeout_settings()
                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info(f"Selected timeout: {label}")
                else:
                    options = [el.text for el in self.d.xpath('//*[@text]').all()]
                    logging.warning(f"Timeout option '{label}' not found. Available: {options}")
                    continue
                time.sleep(2)
                current_timeout = self._get_current_timeout()
                if current_timeout != expected_ms:
                    logging.error(f"Timeout mismatch! Expected {expected_ms}, got {current_timeout}")
                else:
                    logging.info(f"Timeout set correctly to {expected_ms} ms")
                if wait_sec > 0:
                    logging.info(f"Waiting {wait_sec}s for screen-off verification...")
                    time.sleep(wait_sec)
                    if self._is_screen_off():
                        logging.info(f"Screen turned off as expected ({label})")
                        self._wake_up_device()
                    else:
                        logging.warning(f"Screen still ON after {wait_sec}s ({label})")
                # Return to home after each test iteration
                self.d.press("home")
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error testing timeout '{label}': {e}", exc_info=True)

def create_timeout_test(ad: android_device.AndroidDevice,
                        coords: Dict[str, Tuple[int, int]] = None) -> TimeoutTestManager:
    return TimeoutTestManager(ad)