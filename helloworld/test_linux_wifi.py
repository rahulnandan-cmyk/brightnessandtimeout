# filename: test_linux_wifi.py
import subprocess
import time
from mobly import base_test
from mobly import test_runner

class LinuxWiFiTest(base_test.BaseTestClass):

    def setup_class(self):
        # Read tools from TestBed parameters or use defaults
        self.settings_tool = self.user_params.get("settings_tool", "gnome-control-center")
        self.wifi_tool = self.user_params.get("wifi_tool", "nmcli")
        print(f"Using settings tool: {self.settings_tool}")
        print(f"Using Wi-Fi tool: {self.wifi_tool}")

    def test_open_settings(self):
        """Open Settings app non-blocking (Linux desktop)."""
        subprocess.Popen([self.settings_tool])
        print("Settings opened (non-blocking)")
        # time.sleep(5)  # let the GUI load

    def test_open_wifi(self):
        """Open Wi-Fi settings section non-blocking."""
        subprocess.Popen([self.settings_tool, "wifi"])
        print("Wi-Fi section opened (non-blocking)")
        time.sleep(5)  # let the GUI load

    def test_check_wifi_status(self):
        """Check current Wi-Fi status."""
        result = subprocess.run([self.wifi_tool, "radio", "wifi"], capture_output=True, text=True)
        status = result.stdout.strip().lower()
        print("Wi-Fi status:", status)
        assert status in ["enabled", "disabled"], f"Unexpected Wi-Fi status: {status}"

    def test_toggle_wifi(self):
        """Toggle Wi-Fi ON/OFF."""
        try:
            # Check current status
            result = subprocess.run([self.wifi_tool, "radio", "wifi"], capture_output=True, text=True)
            status = result.stdout.strip().lower()
            
            if status == "enabled":
                subprocess.run([self.wifi_tool, "radio", "wifi", "off"], check=True)
                print("Wi-Fi was ON. Now turned OFF")
            else:
                subprocess.run([self.wifi_tool, "radio", "wifi", "on"], check=True)
                print("Wi-Fi was OFF. Now turned ON")
            
            time.sleep(.5)  # wait for change to take effect
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to toggle Wi-Fi: {e}")

    
    def teardown_class(self):
        """Ensure Wi-Fi is ON after all tests."""
        try:
            subprocess.run([self.wifi_tool, "radio", "wifi", "on"], check=True)
            print("Wi-Fi restored to ON state after tests.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to restore Wi-Fi: {e}")

if __name__ == "__main__":
    test_runner.main()
