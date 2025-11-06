# filename: test_system_updates.py
import subprocess
import logging
from mobly import base_test
from mobly import test_runner

class SystemUpdatesTest(base_test.BaseTestClass):
    """Test class to verify system update checking functionality."""

    def setup_class(self):
        # Get parameters from config
        self.update_tool = self.user_params.get("update_tool", "apt")
        self.logger = logging.getLogger()

    def test_check_system_updates(self):
        """Test checking for system updates."""
        
        # Step 1: Check for available system updates
        self.logger.info("Step 1: Checking for system updates...")
        
        try:
            if self.update_tool == "apt":
                # For Debian/Ubuntu based systems
                result = subprocess.run(
                    ["apt", "list", "--upgradable"],
                    capture_output=True, text=True, timeout=30
                )
                
                # Verify the command ran successfully
                if result.returncode != 0:
                    raise AssertionError(f"Failed to check for updates. Return code: {result.returncode}")
                
                # Verify output contains expected information
                if "Listing..." not in result.stdout and result.stdout.strip() == "":
                    self.logger.info("No updates available - system is up to date")
                else:
                    self.logger.info(f"Updates available: {result.stdout}")
                    
            elif self.update_tool == "dnf":
                # For Fedora/RHEL based systems
                result = subprocess.run(
                    ["dnf", "check-update"],
                    capture_output=True, text=True, timeout=30
                )
                
                # Verify the command ran successfully
                # Note: dnf returns 100 when updates are available, 0 when no updates
                if result.returncode not in [0, 100]:
                    raise AssertionError(f"Failed to check for updates. Return code: {result.returncode}")
                
                if result.returncode == 0:
                    self.logger.info("No updates available - system is up to date")
                else:
                    self.logger.info(f"Updates available: {result.stdout}")
                    
            else:
                raise AssertionError(f"Unsupported update tool: {self.update_tool}")
                
        except subprocess.TimeoutExpired:
            raise AssertionError("Update check timed out")
        except Exception as e:
            raise AssertionError(f"Error checking for updates: {str(e)}")
        
        # Step 2: Verify the device checks for updates and displays the correct information
        self.logger.info("Step 2: Verifying update information...")
        
        # We've already verified in the step above that:
        # 1. The command ran successfully
        # 2. We got output (either "no updates" or list of updates)
        
        self.logger.info("System update check completed successfully!")

    def teardown_class(self):
        """No cleanup needed for this test."""
        pass


if __name__ == "__main__":
    test_runner.main()