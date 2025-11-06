import pyautogui
import time
import logging
from mobly import base_test, test_runner

class Setting(base_test.BaseTestClass):
    """
    Mobly test to switch and manage tabs via UI clicks
    """

    def setup_class(self):
        """Setup for the test class."""
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)
        if not self.log.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.log.addHandler(handler)

        self.log.info("Test setup completed")
        pyautogui.FAILSAFE = True

    def teardown_class(self):
        """Teardown after all tests in this class"""
        self.log.info("Test completed")

    def test_setting_privacy(self):
        """Perform UI-based manage and switch between tabs"""
        self.log.info("Clicking system tray")
        pyautogui.moveTo(x=1292, y=4, duration=1)
        pyautogui.click()
        time.sleep(1)
        
        self.log.info("Clicking settings app")
        pyautogui.moveTo(x=1228, y=325, duration=1)
        pyautogui.click()
        time.sleep(1)

        self.log.info("Clicking privacy from settings")
        pyautogui.moveTo(x=341, y=510, duration=1)
        pyautogui.click()
        time.sleep(1)

        self.log.info("Close settings window")
        pyautogui.moveTo(x=1192, y=44, duration=1)
        pyautogui.click()
        time.sleep(1)

if __name__ == "__main__":
    test_runner.main()
