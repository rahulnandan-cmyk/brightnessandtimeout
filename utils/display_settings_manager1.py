#!/usr/bin/env python3
# utils/display_settings_manager1.py
"""Module for managing and testing Android Display Settings."""
import logging
import time
from typing import List

import uiautomator2 as u2
from mobly.controllers import android_device
from uiautomator2 import Device

class DisplaySettingsManager:
    """
    Manages all display-related test setup, execution (Brightness and Timeout),
    and teardown using UIAutomator2 and ADB shell commands.
    """

    # ===== Labels =====
    HOME_KEYWORDS = ["launcher", "home"]
    DISPLAY_LABELS = ["Display", "Settings"]
    BRIGHTNESS_LABELS = ["Brightness level","Display brightness"]
    TIMEOUT_LABELS = ["Screen timeout"]

    # ===== Constants =====
    DEFAULT_TIMEOUT_MS = 30000
    SETTINGS_PACKAGE = "com.android.settings"

    def __init__(self, ad: android_device.AndroidDevice):
        self.ad = ad
        self.d: Device = u2.connect(ad.serial)

        # Initial wake-up to ensure device is responsive
        try:
            for cmd in ["input keyevent KEYCODE_WAKEUP", "input keyevent KEYCODE_MENU"]:
                self.ad.adb.shell(cmd)
                time.sleep(0.5)
            logging.info("Initial wake-up commands sent successfully!")
        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Initial device wake-up failed: %s", e)

    def setup_test(self) -> bool:
        """
        Set up the device for testing (wake, home screen, disable adaptive features).

        :returns: True if setup completed successfully, False otherwise.
        :rtype: bool
        """
        logging.info("=" * 60)
        logging.info("Starting Display Test Setup")
        logging.info("=" * 60)

        try:
            # Global setup for both brightness and timeout tests.
            self.ad.adb.shell("settings put global stay_on_while_plugged_in 0")
            # Disable Adaptive Brightness.
            self.ad.adb.shell("settings put system screen_brightness_mode 0")

            self.wake_up_device()
            self._ensure_home_screen()
            logging.info("Test setup completed successfully")
            return True
        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Test setup failed: %s", e, exc_info=True)
            return False

    def teardown_test(self) -> None:
        """
        Cleans up by resetting timeout to default (30s) and returning to the home screen
        """
        try:
            logging.info("Starting teardown - resetting settings and returning home")
            self.close_settings_dialogs()

            logging.info(
                "Resetting timeout to %d seconds...", self.DEFAULT_TIMEOUT_MS // 1000
            )
            self.ad.adb.shell(
                f"settings put system screen_off_timeout {self.DEFAULT_TIMEOUT_MS}"
            )

        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Teardown failed: %s", e, exc_info=True)

    def scroll_and_click_setting(
            self, setting_labels: List[str], timeout: int = 2) -> None:
        """
        Scrolls the current view to find an element matching any of the given
        labels, clicks it, and raises an error if none are found.
        """
        logging.info(
            "Attempting to find and click settings related to '%s'...", setting_labels
        )

        found_label = None

        # 1. Iterate through all possible labels, scrolling to find each one.
        for label in setting_labels:
            if self.d(scrollable=True).exists:
                # Scroll until the text is found.
                self.d(scrollable=True).scroll.to(textContains=label)

            # 2. Check if the element now exists in the viewport and click it.
            if self.d(textContains=label).exists:
                self.d(textContains=label).click()
                logging.info("Successfully clicked setting with label: '%s'.", label)
                found_label = label
                break

        # 3. Handle total failure if no label was found after all attempts.
        if found_label is None:
            # Error handling fallback: Collect visible options for debugging.
            options = [el.text for el in self.d.xpath("//*[@text]").all()]
            logging.error(
                "None of the required settings (%s) were found! Options: %s",
                setting_labels,
                options,
                exc_info=True,
            )
            raise RuntimeError(
                f"Could not find any of the required settings: {setting_labels}"
            )

        time.sleep(timeout)

    def _ensure_home_screen(self) -> None:
        """Forces the device to the home screen using multiple home presses."""
        logging.info("Ensuring Home Screen...")
        pkg = ""
        for _ in range(3):
            self.d.press("home")
            time.sleep(1)
            pkg = self.d.info.get("currentPackageName", "")
            logging.info("Current package: %s", pkg)
            if any(keyword in pkg.lower() for keyword in self.HOME_KEYWORDS):
                logging.info("Home screen detected: %s", pkg)
                return

        raise RuntimeError(
            f"Home Screen not detected after 3 attempts. package: {pkg}"
        )

    def navigate_to_display_menu(self) -> None:
        """Navigates to the main Display Settings Menu."""
        logging.info("Navigating to Display Settings Menu...")

        # Start Settings App using the new helper method
        self.access_settings_from_launcher()

        found_display = False
        # 1. Try to find element if its visible without scrolling
        for label in self.DISPLAY_LABELS:
            if self.d(text=label).exists:
                self.d(text=label).click()
                logging.info("Opened '%s' settings", label)
                found_display = True
                break

        if not found_display:
            # 2. Scrolling fallback
            # If this fails, the utility function will raise the RuntimeError.
            self.scroll_and_click_setting(setting_labels=self.DISPLAY_LABELS)

        time.sleep(2)

    # === PUBLIC METHODS (Used by API classes) ===

    def wake_up_device(self) -> None:
        """Wakes up the device and dismisses the keyguard"""
        logging.info("Waking up device...")
        self.ad.adb.shell("input keyevent KEYCODE_WAKEUP")
        self.ad.adb.shell("wm dismiss-keyguard")
        time.sleep(2)

    def close_settings_dialogs(self) -> None:
        """Utility to close any open settings dialogs and returns to home."""
        logging.info("Closing any open settings...")
        # Press back multiple times.
        for _ in range(3):
            self.d.press("back")
            time.sleep(0.5)
        # Return to home
        self.d.press("home")
        time.sleep(1)

    def navigate_to_brightness_settings(self) -> None:
        """Navigates from the Display menu to the brightness slider control."""
        self._navigate_to_display_menu()

        found_brightness = False
        # 1. Try to find the element if it's visible without scrolling
        for label in self.BRIGHTNESS_LABELS:
            if self.d(textContains=label).exists:
                self.d(textContains=label).click()
                logging.info("Clicked brightness options: '%s'", label)
                found_brightness = True
                break

        if not found_brightness:
            # 2. Scrolling fallback: If the direct search fails, use the robust utility.
            self.scroll_and_click_setting(setting_labels=self.BRIGHTNESS_LABELS)

        time.sleep(2)

    def open_timeout_settings(self) -> None:
        """Navigates from home to the Screen Timeout setting selection menu"""
        logging.info("Navigating to Screen Timeout Settings...")
        self.close_settings_dialogs()
        self._navigate_to_display_menu()
        self.scroll_and_click_setting(setting_labels=self.TIMEOUT_LABELS)

    def get_brightness(self) -> int:
        """Get current brightness using ADB shell"""
        try:
            result = self.ad.adb.shell("settings get system screen_brightness")
            result_str = (
                result.decode("utf-8").strip()
                if isinstance(result, bytes)
                else str(result).strip()
            )
            return int(result_str) if result_str.isdigit() else -1
        except (ValueError, OSError, RuntimeError) as e:
            logging.error("Failed to get brightness: %s", e)
            return -1

    def get_current_timeout(self) -> int:
        """Retrieves the current screen off timeout value in millisecond via ADB"""
        try:
            result = self.ad.adb.shell("settings get system screen_off_timeout")
            result_str = (
                result.decode("utf-8").strip()
                if isinstance(result, bytes)
                else str(result).strip()
            )
            return int(result_str) if result_str.isdigit() else 0

        except (ValueError, OSError, RuntimeError) as e:
            logging.error("Failed to get timeout: %s", e)
            return 0

    def is_screen_off(self) -> bool:
        """Checks if the device screen is off (Asleep) using dumpsys power."""
        try:
            state = self.ad.adb.shell("dumpsys power | grep mWakefulness")
            state = state.decode("utf-8") if isinstance(state, bytes) else state
            return "Asleep" in state

        except (ValueError, OSError, RuntimeError) as e:
            logging.error("Failed to check screen state: %s", e)
            return False

    def access_settings_from_launcher(self) -> None:
        """Starts the main Android Settings application."""
        logging.info("Starting Android Settings application...")
        # Use the class constant for consistency
        self.d.app_start(self.SETTINGS_PACKAGE)
        time.sleep(3)

    def verify_settings_ui_visible(self) -> bool:
        """
        Verifies that the Settings UI is visible and responsive.

        :returns: True if Settings UI elements are visible, False otherwise
        :rtype: bool
        """
        try:
            # Check if common Settings UI elements are present
            if self.d(textContains="Settings").exists or self.d(textContains="Search").exists:
                logging.info("Settings UI is visible and responsive")
                return True

            logging.warning("Settings UI elements not detected")
            return False
        except (RuntimeError, ValueError, OSError) as err:
            logging.error("Error verifying Settings UI: %s", err)
            return False

    def debug_display_menu(self):
        """Debug what's inside Display settings"""
        self.access_settings_from_launcher()
        self.scroll_and_click_setting(setting_labels=["Display"])
        time.sleep(2)

        # Get ALL text elements inside Display menu
        all_elements = self.d.xpath("//*[@text]").all()
        for el in all_elements:
            if el.text and len(el.text.strip()) > 0:
                logging.info("INSIDE DISPLAY MENU: '%s'", el.text)

    # Add to DisplaySettingsManager class

    def navigate_to_dark_theme_settings(self) -> bool:
        """Navigates to Dark Theme settings in Display menu."""
        logging.info("Navigating to Dark Theme Settings...")

        try:
            # Navigate to Display menu first
            self._navigate_to_display_menu()
            time.sleep(2)

            # Look for Dark Theme option
            dark_theme_labels = [
                "Dark theme",
                "Dark mode",
                "Night mode"
            ]

            self.scroll_and_click_setting(setting_labels=dark_theme_labels)
            logging.info("Successfully opened Dark Theme settings")
            return True

        except Exception as e:
            logging.error("Failed to navigate to Dark Theme settings: %s", e)
            return False

    def set_dark_theme_schedule(self, schedule_type: str, custom_time: str = None) -> bool:
        """
        Sets dark theme schedule.

        Args:
            schedule_type: "sunset_sunrise", "custom_time", or "none"
            custom_time: Time string for custom schedule (e.g., "20:00")

        Returns:
            bool: True if schedule was set successfully
        """
        try:
            if not self.navigate_to_dark_theme_settings():
                return False

            time.sleep(2)

            # Click on Schedule option
            schedule_labels = ["Schedule", "Set schedule"]
            self.scroll_and_click_setting(setting_labels=schedule_labels)
            time.sleep(2)

            if schedule_type == "sunset_sunrise":
                sunset_labels = ["Turns on from sunset to sunrise", "Sunset to sunrise"]
                self.scroll_and_click_setting(setting_labels=sunset_labels)

            elif schedule_type == "custom_time":
                custom_labels = ["Turns on at custom time", "Custom schedule"]
                self.scroll_and_click_setting(setting_labels=custom_labels)
                # Custom time setting would go here

            elif schedule_type == "none":
                none_labels = ["None", "Off", "Never"]
                self.scroll_and_click_setting(setting_labels=none_labels)

            logging.info("Dark Theme schedule set to: %s", schedule_type)
            return True

        except Exception as e:
            logging.error("Failed to set Dark Theme schedule: %s", e)
            return False

    def is_dark_theme_enabled(self) -> bool:
        """Checks if dark theme is currently enabled via ADB."""
        try:
            result = self.ad.adb.shell("settings get secure dark_mode")
            return result.strip() == "1"
        except Exception as e:
            logging.error("Failed to check dark theme status: %s", e)
            return False




# Factory function for mobly
def create_display_settings_manager(ad: android_device.AndroidDevice) -> DisplaySettingsManager:
    """Factory function to create a DisplaySettingsManager instance"""
    return DisplaySettingsManager(ad)

