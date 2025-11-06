import pyautogui
import time
import logging
from mobly import base_test, test_runner

class VideoPlayLinuxTest(base_test.BaseTestClass):
    """
    Mobly test to verify launcher using UI
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

        self.log.info("Test setup complete.")
        pyautogui.FAILSAFE = True  

    def teardown_class(self):
        """Teardown after all tests in this class"""
        print("Test teardown complete")

    def test_video_play(self):
        """Playing and ensuring a video play"""
        self.log.info("Open a browser")
        pyautogui.moveTo(x=592, y=1024, duration=1)
        pyautogui.click()
        time.sleep(1)

        self.log.info("Opening new Chrome browser")
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(1)

        self.log.info("Open youtube")
        pyautogui.typewrite("YouTube")
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(5)
        x, y = pyautogui.position()  # Get current cursor coordinates
        print(f"Cursor is at: ({x}, {y})")

        self.log.info("Playing a video")
        pyautogui.moveTo(x=772, y=139, duration=1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.typewrite("google demo video")
        pyautogui.hotkey("enter")
        time.sleep(2)

        pyautogui.moveTo(x=709, y=647, duration=1)
        pyautogui.click()
        time.sleep(2)

        self.log.info("Close chrome browser")
        time.sleep(10)
        pyautogui.hotkey('ctrl','W')
        # x, y = pyautogui.position()  # Get current cursor coordinates
        # print(f"Cursor is at: ({x}, {y})")

if __name__ == "__main__":
    test_runner.main()