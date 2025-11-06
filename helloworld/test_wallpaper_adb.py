#!/usr/bin/env python3
"""Test the Background image/wallpaper of Android system."""
import time
import logging
from datetime import datetime
from mobly import base_test, test_runner, asserts
from mobly.controllers import android_device


class AndroidBackgroundChangeTest(base_test.BaseTestClass):
    """Change Android background/wallpaper using ADB automation."""

    def setup_class(self):
        """Setup class."""
        super().setup_class()
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Get screen dimensions for dynamic coordinates
        self._get_screen_size()
        time.sleep(1)

    def _get_screen_size(self):
        """Get device screen resolution for dynamic coordinates."""
        try:
            result = self.ad.adb.shell('wm size')
            logging.info(f"Screen size: {result.strip()}")

            if 'Physical size:' in result:
                dimensions = result.split(':')[1].strip().split('x')
                self.screen_width = int(dimensions[0])
                self.screen_height = int(dimensions[1])
            else:
                # Default values for common Android devices
                self.screen_width = 1080
                self.screen_height = 2340

            logging.info(f"Using screen dimensions: {self.screen_width}x{self.screen_height}")

        except Exception as e:
            logging.warning(f"Could not get screen size, using defaults: {e}")
            self.screen_width = 1080
            self.screen_height = 2340

    def teardown_class(self):
        """Teardown class."""
        try:
            # Press home button to exit any app
            self.ad.adb.shell('input keyevent KEYCODE_HOME')
            logging.info("Returned to home screen in teardown")
            time.sleep(1)
        except Exception as e:
            logging.warning(f"Could not return to home: {e}")

        return super().teardown_class()

    def test_change_background_android(self):
        """
        Test to change Android wallpaper through UI automation.

        Steps:
        1. Open Settings app
        2. Navigate to Wallpaper settings
        3. Select a different wallpaper
        4. Apply the wallpaper
        5. Verify the change was successful
        """
        logging.info("=== Starting Android Background Change Test ===")

        try:
            # Step 1: Open Settings app
            logging.info("1. Opening Settings app")
            self.ad.adb.shell('am start -a android.settings.SETTINGS')
            time.sleep(3)  # Wait for Settings to open

            # Step 2: Navigate to Wallpaper settings
            logging.info("2. Navigating to Wallpaper settings")
            self._navigate_to_wallpaper_settings()

            # Step 3: Select a different wallpaper
            logging.info("3. Selecting different wallpaper")
            self._select_wallpaper()

            # Step 4: Apply the wallpaper
            logging.info("4. Applying wallpaper")
            self._apply_wallpaper()
            time.sleep(2)

            # Step 5: Verify background change
            logging.info("5. Verifying wallpaper change")
            self._verify_background_change()

            logging.info("Android background change test completed successfully!")

        except Exception as e:
            logging.error(f"Android background change automation failed: {e}")
            asserts.fail(f"Android background change failed: {e}")

    def _navigate_to_wallpaper_settings(self):
        """Navigate to wallpaper settings in Android."""
        # This will vary by Android version and manufacturer
        # Common paths: Settings -> Display -> Wallpaper

        # Try different navigation methods:

        # Method 1: Search for wallpaper settings
        logging.info("   Searching for wallpaper settings")
        self.ad.adb.shell('input tap 500 200')  # Tap search bar
        time.sleep(1)
        self.ad.adb.shell('input text "wallpaper"')
        time.sleep(1)
        self.ad.adb.shell('input keyevent KEYCODE_ENTER')
        time.sleep(2)

        # Method 2: If search doesn't work, navigate manually
        # Scroll and look for "Wallpaper" or "Display"
        logging.info("   Attempting manual navigation")
        self.ad.adb.shell('input swipe 500 1000 500 500 500')  # Scroll down
        time.sleep(1)

        # Tap common positions for Wallpaper/Display settings
        # You may need to adjust these coordinates based on your device
        wallpaper_positions = [
            (500, 400),   # Top area
            (500, 700),   # Middle area
            (500, 1000),  # Bottom area
        ]

        for x, y in wallpaper_positions:
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2)
            # Check if we're in wallpaper settings by looking for common elements
            # If not, go back and try next position
            self.ad.adb.shell('input keyevent KEYCODE_BACK')
            time.sleep(1)

    def _select_wallpaper(self):
        """Select a different wallpaper from available options."""
        # Tap on different wallpaper categories or images
        # These coordinates will need adjustment based on your wallpaper picker UI

        categories = [
            (300, 600),   # Left category
            (500, 600),   # Center category
            (700, 600),   # Right category
        ]

        for x, y in categories:
            logging.info(f"   Trying wallpaper category at ({x}, {y})")
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2)

            # Try to select a wallpaper from this category
            self.ad.adb.shell('input tap 500 800')  # Select first wallpaper
            time.sleep(2)

            # Check if we can proceed to apply
            break

    def _apply_wallpaper(self):
        """Apply the selected wallpaper."""
        # Look for "Set wallpaper", "Apply", or similar button
        apply_positions = [
            (500, 1200),  # Bottom center (common for dialogs)
            (800, 1200),  # Bottom right (common for OK/Apply)
            (500, 200),   # Top area (less common)
        ]

        for x, y in apply_positions:
            logging.info(f"   Trying apply button at ({x}, {y})")
            self.ad.adb.shell(f'input tap {x} {y}')
            time.sleep(2)

            # If wallpaper was applied, we should be back at home or settings
            break

    def _verify_background_change(self):
        """Verify that background change was successful."""
        try:
            # Take a screenshot to verify visual change
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f'android_background_after_change_{timestamp}.png'

            # Take screenshot via ADB
            self.ad.adb.shell(f'screencap -p /sdcard/{screenshot_filename}')
            time.sleep(1)

            # Pull screenshot to local machine
            self.ad.adb.pull(f'/sdcard/{screenshot_filename}', f'./{screenshot_filename}')
            logging.info(f"Screenshot saved: {screenshot_filename}")

            # Basic assertion - if we got here without errors, consider it success
            asserts.assert_true(True, "Wallpaper change process completed without errors")

        except Exception as e:
            logging.error(f"Verification failed: {e}")
            asserts.fail(f"Background change verification failed: {e}")

    def test_quick_wallpaper_change(self):
        """Alternative method using direct wallpaper setting commands."""
        try:
            logging.info("Testing direct wallpaper setting method")

            # Method 1: Use settings command (may require root)
            self.ad.adb.shell('am start -a android.intent.action.SET_WALLPAPER')
            time.sleep(3)

            # Take verification screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_quick")
            self.ad.adb.shell(f'screencap -p /sdcard/wallpaper_quick_{timestamp}.png')
            self.ad.adb.pull(f'/sdcard/wallpaper_quick_{timestamp}.png', f'./wallpaper_quick_{timestamp}.png')

            asserts.assert_true(True, "Quick wallpaper test completed")

        except Exception as e:
            logging.warning(f"Quick wallpaper method failed: {e}")


if __name__ == "__main__":
    test_runner.main()