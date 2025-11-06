from mobly import base_test
from mobly import test_runner
import subprocess

class EmulatorUITest(base_test.BaseTestClass):

    def setup_class(self):
        # FIX: Use self.logger instead of self.log in setup_class
        self.logger.info("Checking connected devices...")
        output = subprocess.check_output(["adb", "devices"]).decode().splitlines()
        self.logger.info("\n".join(output))

    def test_launch_calculator(self):
        """Launch calculator app"""
        subprocess.run([
            "adb", "shell", "monkey",
            "-p", "com.android.calculator2",
            "-c", "android.intent.category.LAUNCHER",
            "1"
        ])
        # FIX: Also use self.logger in test methods for consistency and to avoid potential issues
        self.logger.info("Launched Calculator app")

if __name__ == "__main__":
    test_runner.main()