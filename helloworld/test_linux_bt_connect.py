# test_linux_bt_connect.py
import subprocess
from mobly import base_test, test_runner, asserts

class LinuxBluetoothTest(base_test.BaseTestClass):
    """Mobly test to connect to a Bluetooth device on Linux."""

    def setup_class(self):
        super().setup_class()
        self.device_mac = "41:42:07:79:BB:BD"
        self.log.info(f"Target Bluetooth device: {self.device_mac}")
    
    def test_bt_connect(self):
        """Test connecting to the Bluetooth device."""
        self.log.info("Powering on Bluetooth...")
        # Check and turn on Bluetooth
        power_on_result = subprocess.run("bluetoothctl power on", shell=True, check=True)
        asserts.assert_equal(power_on_result.returncode, 0, "Failed to power on Bluetooth adapter.")
        
        self.log.info("Pairing device...")
        # Pair with the device
        pair_result = subprocess.run(f"bluetoothctl pair {self.device_mac}", shell=True, check=True)
        asserts.assert_equal(pair_result.returncode, 0, "Failed to pair with device.")
        
        self.log.info("Trusting device...")
        # Trust the device for automatic future connections
        trust_result = subprocess.run(f"bluetoothctl trust {self.device_mac}", shell=True, check=True)
        asserts.assert_equal(trust_result.returncode, 0, "Failed to trust device.")

        self.log.info("Connecting device...")
        # Connect to the device
        connect_result = subprocess.run(
            f"bluetoothctl connect {self.device_mac}",
            shell=True,
            capture_output=True,
            text=True
        )
        self.log.info(f"bluetoothctl output:\n{connect_result.stdout}")

        asserts.assert_in(
            "Connection successful", connect_result.stdout,
            "Failed to connect to Bluetooth device!"
        )

    def teardown_class(self):
        super().teardown_class()
        self.log.info(f"Disconnecting {self.device_mac}...")
        subprocess.run(f"bluetoothctl disconnect {self.device_mac}", shell=True, check=False)

if __name__ == "__main__":
    test_runner.main()