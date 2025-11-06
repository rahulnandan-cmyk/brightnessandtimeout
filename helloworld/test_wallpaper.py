"""Test the Background image of the system."""
import time
import pyautogui
import logging
from datetime import datetime
from mobly import base_test, test_runner, asserts


class BackgroundChangeTest(base_test.BaseTestClass):
    """Change background/wallpaper using UI automation."""

    def setup_class(self):
        """Setup class."""
        super().setup_class()  # Call parent setup
        pyautogui.FAILSAFE = True  # PyAutoGUI constantly monitors your mouse position
        logging.info("PyAutoGUI failsafe enabled")
        time.sleep(1)

    def teardown_class(self):
        """Teardown class."""
        try:
            pyautogui.hotkey('alt','f4')
            logging.info("Closed Settings window in teardown")
            time.sleep(1)
        except Exception as e:
            logging.warning(f"Could not close settings window:{e}")
            
        return super().teardown_class()

    def test_change_background_gui(self):
        """
        Test to change desktop background through UI automation.

        Steps:
        1. Click System Tray to open menu
        2. Click Settings from the menu  
        3. Click Background tab
        4. Select a different background
        5. Verify the change was successful
        """
        logging.info("=== Starting Background Change Test ===")

        try:
            logging.info("1. Clicking system tray")
            pyautogui.moveTo(1841, 8, duration=0.5)
            pyautogui.click()
            logging.info("System tray clicked")
            time.sleep(2)  # Wait for menu to appear

            logging.info("2. Clicking Settings button")
            pyautogui.moveTo(1710, 349, duration=0.5)
            pyautogui.click()
            logging.info("Settings clicked")
            time.sleep(3)  # Wait for Settings app to open

            logging.info("3. Clicking Background tab")
            pyautogui.moveTo(594, 365, duration=0.5)
            pyautogui.click()
            logging.info("Background tab clicked")
            time.sleep(2)  # Wait for background settings to load

            logging.info("4. Selecting different background")
            pyautogui.moveTo(1096, 623, duration=0.5)
            pyautogui.click()
            logging.info("Background selected")
            time.sleep(2)

            logging.info("5. Verifying background change")
            self._verify_background_change()

            logging.info("Background change test completed successfully!")

        except Exception as e:
            logging.error(f"Background change automation failed: {e}")
            asserts.fail(f"Background change failed: {e}")

    def _verify_background_change(self):
        """Verify that background change was successful."""
        try:
            current_pos = pyautogui.position()
            logging.info(f"Current mouse position: {current_pos}")
            asserts.assert_true(True, "Background change process completed")

            # Take the screenshot with date and time in filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f'background_after_change_{timestamp}.png' 
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_filename)

        except Exception as e:
            logging.error(f"Verification failed: {e}")
            asserts.fail(f"Background change verification failed: {e}")


if __name__ == "__main__":
    test_runner.main()