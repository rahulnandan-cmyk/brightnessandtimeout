# filename: test_linux_bt.py
import subprocess
from mobly import base_test
from mobly import test_runner

class LinuxBluetoothTest(base_test.BaseTestClass):

    def setup_class(self):
        # Verify Bluetooth is installed
        subprocess.run("which bluetoothctl", shell=True, check=True)

    def test_open_settings(self):
        """Open Settings app (Linux desktop)."""
        # This will work if `gnome-control-center` is available
        subprocess.run("gnome-control-center", shell=True)

    def test_open_bluetooth(self):
        """Open Bluetooth settings window directly."""
        # GNOME command to open Bluetooth settings
        subprocess.run("gnome-control-center bluetooth", shell=True)

    def test_check_bt_status(self):
        """Check if Bluetooth service is running."""
        result = subprocess.run("systemctl is-active bluetooth", 
                                shell=True, capture_output=True, text=True)
        print("Bluetooth service status:", result.stdout.strip())
        assert result.stdout.strip() == "active", "Bluetooth service not active!"

if __name__ == "__main__":
    test_runner.main()
