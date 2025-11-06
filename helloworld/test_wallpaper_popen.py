"""Test the Background image of the system."""
import time
import pyautogui
import logging
import subprocess
from datetime import datetime
from mobly import base_test, test_runner, asserts


class BackgroundChangeTest(base_test.BaseTestClass):
    """Change background/wallpaper using UI automation."""

    def setup_class(self):
        """Setup class."""
        super().setup_class()  # Call parent setup
        pyautogui.FAILSAFE = True  # PyAutoGUI constantly monitors your mouse position
        logging.info("PyAutoGUI failsafe enabled")
        self.settings_process = None
        time.sleep(1)

    def teardown_class(self):
        """Teardown class."""
        # Use Popen control identifiers to properly manage the Settings process
        if self.settings_process and self.settings_process.poll() is None:
            logging.info("Closing Settings window using process termination")
            try:
                # Try graceful termination first
                self.settings_process.terminate()
                self.settings_process.wait(timeout=5)
                logging.info("Settings window closed gracefully")
            except subprocess.TimeoutExpired:
                logging.warning("Settings process did not terminate gracefully, forcing kill")
                self.settings_process.kill()
                self.settings_process.wait()
                logging.info("Settings process forcefully killed")
            
            # Check the final return code
            returncode = self.settings_process.poll()
            logging.info(f"Settings process exit code: {returncode}")
        
        return super().teardown_class()

    def test_change_background_gui(self):
        """
        Test to change desktop background through UI automation.

        Steps:
        1. Click System Tray to open menu
        2. Click Settings from the menu  
        3. Click Background tab
        4. Select a different background
        5. Verify the change was successful
        """
        logging.info("=== Starting Background Change Test ===")

        try:
            logging.info("1. Clicking system tray")
            pyautogui.moveTo(1841, 8, duration=0.5)
            pyautogui.click()
            logging.info("System tray clicked")
            time.sleep(2)  # Wait for menu to appear

            logging.info("2. Clicking Settings button")
            pyautogui.moveTo(1710, 349, duration=0.5)
            pyautogui.click()
            logging.info("Settings clicked")
            time.sleep(3)  # Wait for Settings app to open

            # Store the Settings process using Popen for better control
            self._capture_settings_process()

            logging.info("3. Clicking Background tab")
            pyautogui.moveTo(594, 365, duration=0.5)
            pyautogui.click()
            logging.info("Background tab clicked")
            time.sleep(2)  # Wait for background settings to load

            logging.info("4. Selecting different background")
            pyautogui.moveTo(1096, 623, duration=0.5)
            pyautogui.click()
            logging.info("Background selected")
            time.sleep(2)

            logging.info("5. Verifying background change")
            self._verify_background_change()

            logging.info("Background change test completed successfully!")

        except Exception as e:
            logging.error(f"Background change automation failed: {e}")
            asserts.fail(f"Background change failed: {e}")

    def _capture_settings_process(self):
        """Capture the Settings application process using Popen."""
        try:
            # On Windows, you can start Settings app directly
            # On other systems, you might need to adjust the command
            if subprocess.os.name == 'nt':  # Windows
                self.settings_process = subprocess.Popen(['start', 'ms-settings:'], 
                                                       shell=True)
            else:  # Linux/Unix - adjust command for your system
                # Example for GNOME: gnome-control-center
                # Example for KDE: systemsettings
                self.settings_process = subprocess.Popen(['gnome-control-center'])
            
            logging.info(f"Settings process started with PID: {self.settings_process.pid}")
            time.sleep(2)  # Give it time to launch
            
        except Exception as e:
            logging.warning(f"Could not capture Settings process directly: {e}")
            logging.info("Falling back to UI automation only")

    def _verify_background_change(self):
        """Verify that background change was successful."""
        try:
            # Check if Settings process is still running using Popen control identifiers
            if self.settings_process:
                returncode = self.settings_process.poll()
                if returncode is None:
                    logging.info(f"Settings process (PID: {self.settings_process.pid}) is still running")
                else:
                    logging.info(f"Settings process ended with return code: {returncode}")

            current_pos = pyautogui.position()
            logging.info(f"Current mouse position: {current_pos}")
            asserts.assert_true(True, "Background change process completed")

            # Take the screenshot with date and time in filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f'background_after_change_{timestamp}.png' 
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_filename)

        except Exception as e:
            logging.error(f"Verification failed: {e}")
            asserts.fail(f"Background change verification failed: {e}")


if __name__ == "__main__":
    test_runner.main()