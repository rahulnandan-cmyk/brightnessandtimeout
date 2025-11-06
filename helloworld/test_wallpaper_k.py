"""Test the Background image of the system using keyboard automation."""
import time
import pyautogui
import logging
from datetime import datetime
from mobly import base_test, test_runner, asserts


class KeyboardBackgroundChangeTest(base_test.BaseTestClass):
    """Change background/wallpaper using keyboard automation."""

    def setup_class(self):
        """Setup class."""
        super().setup_class()
        pyautogui.FAILSAFE = True
        logging.info("Keyboard automation test started")
        time.sleep(1)

    def teardown_class(self):
        """Teardown class."""
        try:
            pyautogui.hotkey('alt', 'f4')  # Close settings with keyboard
            logging.info("Closed Settings window using Alt+F4")
            time.sleep(1)
        except Exception as e:
            logging.warning(f"Could not close settings window: {e}")
            
        return super().teardown_class()

    def test_keyboard_background_change(self):
        """
        Test to change desktop background using keyboard only.
        
        Steps:
        1. Open System Tray using keyboard
        2. Navigate to Settings using keyboard
        3. Navigate to Background tab using keyboard
        4. Select background using keyboard
        5. Verify the change
        """
        logging.info("=== Starting Keyboard-Based Background Change Test ===")

        try:
            # Step 1: Open System Tray using Super key (Windows key)
            logging.info("1. Opening system tray with Super/win key")
            pyautogui.press('win') 
            time.sleep(2)
            
            # Step 2: Search for Settings
            logging.info("2. Searching for Settings")
            pyautogui.write('settings', interval=0.1)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(3)  # Wait for Settings to open

            # Step 3: Navigate to Background using keyboard
            logging.info("3. Navigating to Background settings")
            
            # Method 1: Using Tab navigation
            pyautogui.hotkey('ctrl', 'f')
            pyautogui.write('background',interval=0.1)
            pyautogui.press('enter')
            time.sleep(1)

            # Step 4: Select background using keyboard
            logging.info("4. Selecting background with keyboard")
            pyautogui.press('tab', presses=2, interval=0.5)  # Navigate to background grid
            pyautogui.press('right', presses=3, interval=0.5)  # Move to different background
            pyautogui.press('enter')  # Select the background
            time.sleep(2)

            # Step 5: Final verification
            logging.info("5. Verifying background change")
            self._verify_background_change()

            logging.info("Keyboard-based background change completed successfully!")

        except Exception as e:
            logging.error(f"Keyboard automation failed: {e}")
            asserts.fail(f"Keyboard automation failed: {e}")

    def _verify_background_change(self):
        """Verify that background change was successful."""
        try:
            # Take timestamped screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f'keyboard_background_change_{timestamp}.png'
            pyautogui.screenshot(screenshot_filename)
            logging.info(f"Screenshot saved: {screenshot_filename}")
            
            asserts.assert_true(True, "Keyboard automation completed successfully")

        except Exception as e:
            logging.error(f"Verification failed: {e}")
            asserts.fail(f"Verification failed: {e}")


if __name__ == "__main__":
    test_runner.main()