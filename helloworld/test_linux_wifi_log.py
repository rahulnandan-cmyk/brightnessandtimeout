# filename: test_linux_wifi_log.py
import subprocess
import time
import logging
from mobly import base_test
from mobly import test_runner

# Module-level logger
logger = logging.getLogger(__name__)

class LinuxWiFiTest(base_test.BaseTestClass):

    def setup_class(self):
        self.settings_tool = self.user_params.get("settings_tool", "gnome-control-center")
        self.wifi_tool = self.user_params.get("wifi_tool", "nmcli")
        logger.info(f"Using settings tool: {self.settings_tool}")
        logger.info(f"Using Wi-Fi tool: {self.wifi_tool}")

    def test_open_settings(self):
        subprocess.Popen([self.settingste_tool])
        logger.info("Settings opened (non-blocking)")
        time.sleep(5)

    def test_open_wifi(self):
        subprocess.Popen([self.settings_tool, "wifi"])
        logger.info("Wi-Fi section opened (non-blocking)")
        time.sleep(5)

    def test_check_wifi_status(self):
        result = subprocess.run([self.wifi_tool, "radio", "wifi"],
                                capture_output=True, text=True)
        status = result.stdout.strip().lower()
        logger.info(f"Wi-Fi status: {status}")
        assert status in ["enabled", "disabled"], f"Unexpected Wi-Fi status: {status}"

    def test_toggle_wifi(self):
        try:
            result = subprocess.run([self.wifi_tool, "radio", "wifi"],
                                    capture_output=True, text=True)
            status = result.stdout.strip().lower()
            
            if status == "enabled":
                subprocess.run([self.wifi_tool, "radio", "wifi", "off"], check=True)
                logger.info("Wi-Fi was ON. Now turned OFF")
                time.sleep(5)
            else:
                subprocess.run([self.wifi_tool, "radio", "wifi", "on"], check=True)
                logger.info("Wi-Fi was OFF. Now turned ON")
            
            time.sleep(5)
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to toggle Wi-Fi: {e}")
    
    def teardown_class(self):
        try:
            subprocess.run([self.wifi_tool, "radio", "wifi", "on"], check=True)
            result = subprocess.run([self.wifi_tool, "radio", "wifi"],
                                    capture_output=True, text=True)
            status = result.stdout.strip().lower()
            if status == "enabled":
                logger.info("Wi-Fi restored to ON state after tests")
            else:
                logger.error(f"Wi-Fi could not be restored, status={status}")
                self.fail(f"Wi-Fi could not be restored, status={status}")
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to restore Wi-Fi in teardown: {e}")

if __name__ == "__main__":
    test_runner.main()