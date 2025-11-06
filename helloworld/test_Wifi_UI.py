# filename: test_linux_wifi_ui.py
import time
import subprocess
import pyautogui
from mobly import base_test, test_runner, asserts

class LinuxWiFiUITest(base_test.BaseTestClass):

    def setup_class(self):
        # Important: Initialize Mobly base class first
        super().setup_class()

        # Load test parameters
        self.settings_tool = self.user_params.get("settings_tool", "gnome-control-center")
        self.log.info(f"Using settings tool: {self.settings_tool}")


    def test_open_settings(self):
        """Open the Settings UI app."""
        subprocess.Popen(self.settings_tool, shell=True)
        time.sleep(3)  # wait for Settings window to appear

    def test_open_wifi_ui(self):
        """Navigate to the Wi-Fi section in Settings using UI automation."""
        # Press ALT+F2 to trigger GNOME run dialog, type wifi
        pyautogui.hotkey("alt", "f2")
        time.sleep(1)
        pyautogui.typewrite("gnome-control-center wifi")
        pyautogui.press("enter")
        time.sleep(3)

    def test_toggle_wifi_ui(self):
        """Click Wi-Fi toggle in Settings UI."""
        # Locate Wi-Fi switch image (you need a screenshot of the toggle button)
        wifi_toggle = pyautogui.locateOnScreen("wifi_toggle.png", confidence=0.8)
        asserts.assert_is_not_none(wifi_toggle, "Wi-Fi toggle not found on screen")

        # Click the toggle
        pyautogui.click(wifi_toggle)
        time.sleep(2)

        self.log.info("Wi-Fi toggle clicked via UI automation.")

    def teardown_class(self):
        # Close Settings window gracefully
        pyautogui.hotkey("alt", "f4")

if __name__ == "__main__":
    test_runner.main()
