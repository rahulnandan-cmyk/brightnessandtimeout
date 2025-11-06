from mobly import base_test
from mobly import test_runner
import pyautogui
import subprocess
import logging
import time
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class BluetoothTest(base_test.BaseTestClass):
    """Mobly test to toggle Bluetooth ON/OFF via OpenCV UI with CLI fallback."""

    TOGGLE_ON_IMAGE = "bluetooth_toggle_on.png"
    TOGGLE_OFF_IMAGE = "bluetooth_toggle_off.png"

    def setup_class(self):
        logging.info("=== Bluetooth ON/OFF Test Started ===")
        # Ensure Bluetooth service is active
        # subprocess.run(["sudo", "systemctl", "start", "bluetooth"], check=False)
        subprocess.run(["rfkill", "unblock", "bluetooth"], check=False)
        time.sleep(1)

        # Check toggle images exist
        if not os.path.exists(self.TOGGLE_ON_IMAGE) or not os.path.exists(self.TOGGLE_OFF_IMAGE):
            raise FileNotFoundError(
                f"Toggle images not found. Place {self.TOGGLE_ON_IMAGE} and {self.TOGGLE_OFF_IMAGE} in the script folder."
            )

    def get_bluetooth_status(self) -> bool:
        """Check current Bluetooth status via CLI."""
        try:
            result = subprocess.run(
                ["bluetoothctl", "show"], capture_output=True, text=True, check=True
            )
            return any("Powered: yes" in line for line in result.stdout.splitlines())
        except subprocess.CalledProcessError:
            logging.error("Failed to get Bluetooth status")
            return False

    def toggle_bluetooth_ui(self, target: bool) -> bool:
        """Toggle Bluetooth using OpenCV UI detection. Returns True if successful."""
        logging.info(f"Attempting to toggle Bluetooth {'ON' if target else 'OFF'} via UI...")

        image_file = self.TOGGLE_ON_IMAGE if target else self.TOGGLE_OFF_IMAGE

        try:
            # Try to locate the toggle on screen with confidence
            location = pyautogui.locateCenterOnScreen(image_file, confidence=0.8)
            if location:
                pyautogui.click(location)
                time.sleep(2)
                if self.get_bluetooth_status() == target:
                    logging.info(f"Bluetooth successfully toggled {'ON' if target else 'OFF'} via UI")
                    return True
                else:
                    logging.warning("UI toggle attempted but status did not change")
                    return False
            else:
                logging.warning("UI toggle image not found on screen")
                return False
        except Exception as e:
            logging.warning(f"UI toggle exception: {e}")
            return False

    def toggle_bluetooth_cli(self, target: bool):
        """Toggle Bluetooth via CLI fallback."""
        cmd = "on" if target else "off"
        logging.info(f"Toggling Bluetooth {'ON' if target else 'OFF'} via CLI fallback")
        subprocess.run(["bluetoothctl", "power", cmd], check=True)
        time.sleep(1)

    def open_bluetooth_settings(self):
        """Open Bluetooth settings via search."""
        logging.info("Opening Bluetooth Settings...")
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("Settings")
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.write("Bluetooth")
        pyautogui.press("enter")
        time.sleep(1.5)

    def close_settings(self):
        """Close Settings window."""
        pyautogui.hotkey("alt", "f4")
        time.sleep(1)
        logging.info("Closed Settings window")

    def toggle_bluetooth(self, target: bool):
        """Try UI first, then CLI fallback if needed."""
        if not self.toggle_bluetooth_ui(target):
            self.toggle_bluetooth_cli(target)

        # Verify final state
        assert self.get_bluetooth_status() == target, f"Bluetooth did not turn {'ON' if target else 'OFF'}"

    def test_toggle_bluetooth_on_off(self):
        """Test: Turn Bluetooth ON, then OFF, using OpenCV UI + CLI fallback."""
        self.open_bluetooth_settings()
        logging.info("Turning Bluetooth ON...")
        self.toggle_bluetooth(True)

        logging.info("Turning Bluetooth OFF...")
        self.toggle_bluetooth(False)

        self.close_settings()
        logging.info("✅ Bluetooth ON → OFF test completed successfully")


if __name__ == "__main__":
    test_runner.main()

