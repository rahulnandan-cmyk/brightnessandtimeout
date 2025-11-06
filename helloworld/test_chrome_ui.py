# filename: test_chrome_ui.py
import time
import subprocess
import pyautogui
from mobly import base_test, test_runner

class ChromeUITest(base_test.BaseTestClass):

    def setup_class(self):
        super().setup_class()
        # Read Chrome command from testbed.yaml or fallback to default
        self.chrome_cmd = self.user_params.get("chrome_cmd", "google-chrome")
        self.log.info(f"Using Chrome command: {self.chrome_cmd}")

    def test_open_chrome(self):
        """Launch Chrome browser."""
        subprocess.Popen(self.chrome_cmd, shell=True)
        time.sleep(3)  # wait for Chrome window to appear
        self.log.info("Chrome launched successfully")

    def test_open_new_tab(self):
        """Open a new tab in Chrome using Ctrl+T."""
        pyautogui.hotkey("ctrl", "t")
        time.sleep(2)
        self.log.info("New tab opened in Chrome")

    def test_open_url(self):
        """Type a URL in the new tab."""
        pyautogui.typewrite("https://www.google.com")
        pyautogui.press("enter")
        time.sleep(3)
        self.log.info("Google opened in Chrome tab")

    def teardown_class(self):
        super().teardown_class()
        # Close Chrome using Ctrl+Q (Linux shortcut)
        pyautogui.hotkey("ctrl", "q")
        self.log.info("Chrome closed")

if __name__ == "__main__":
    test_runner.main()
