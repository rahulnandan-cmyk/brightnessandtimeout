# filename: test_split_screen_functionality.py
import subprocess
import time
import pyautogui
from mobly import base_test
from mobly import test_runner

# Configure PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Add small delay between actions for reliability

class SplitScreenFunctionalityTest(base_test.BaseTestClass):
    """Test class to verify Split Screen functionality using Settings app."""

    def setup_class(self):
        # Get parameters from config
        self.settings_app = self.user_params.get("settings_app", "gnome-terminal")
        self.gui_load_delay = int(self.user_params.get("gui_load_delay", 3))
        self.action_delay = int(self.user_params.get("action_delay", 1))
        
        self.process = None
        self.terminal_window = None
        
        # Verify we're on a ChromeOS environment
        try:
            result = subprocess.run(["grep", "CHROMEOS", "/etc/lsb-release"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.log.warning("Not running on ChromeOS environment")
        except Exception as e:
            self.log.warning(f"Could not verify ChromeOS environment: {e}")

    def test_split_screen_functionality(self):
        """Verify Split Screen functionality using Settings app."""
        
        # Step 1: Launch the Settings app
        self.log.info("Step 1: Launching Settings app...")
        self.process = subprocess.Popen([self.settings_app])
        time.sleep(self.gui_load_delay)
        
        # Find terminal window
        possible_titles = ["Terminal", self.settings_app]
        windows = []
        for title in possible_titles:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                break
                
        if not windows:
            raise AssertionError("Could not find terminal window")
            
        self.terminal_window = windows[0]
        self.log.info(f"Found terminal window: {self.terminal_window.title}")
        
        # Step 2: Press the Recents key to go to the Overview screen
        self.log.info("Step 2: Pressing Recents key...")
        pyautogui.hotkey('alt', 'tab')  # Simulate Recents key
        time.sleep(self.action_delay)
        
        # Step 3: Tap on the App icon of the Settings app in the Overview
        self.log.info("Step 3: Tapping on Settings app icon in Overview...")
        # This is a simplified approach - in real implementation you'd need to locate the actual UI element
        # For now, we'll simulate the action with a key combination
        pyautogui.hotkey('ctrl', 'shift', 's')  # Simulate split screen activation
        time.sleep(self.action_delay)
        
        # Step 4: Tap on the "Split screen" option
        self.log.info("Step 4: Tapping on Split screen option...")
        # Again, this is a simulation - real implementation would locate the UI element
        pyautogui.press('enter')  # Confirm split screen selection
        time.sleep(self.action_delay)
        
        # Step 5: Verify the Settings app is in Split Screen mode
        self.log.info("Step 5: Verifying Split Screen mode...")
        # In a real implementation, we would check for split screen indicators
        # For this example, we'll verify window geometry changes
        
        # Get current window dimensions
        current_width = self.terminal_window.width
        current_height = self.terminal_window.height
        screen_width, screen_height = pyautogui.size()
        
        # Verify window takes approximately half the screen
        width_ratio = current_width / screen_width
        height_ratio = current_height / screen_height
        
        self.log.info(f"Screen size: {screen_width}x{screen_height}")
        self.log.info(f"Window size: {current_width}x{current_height}")
        self.log.info(f"Width ratio: {width_ratio:.2f}, Height ratio: {height_ratio:.2f}")
        
        # Allow for some tolerance in window sizing
        assert 0.4 <= width_ratio <= 0.6, (
            f"Window width ratio {width_ratio:.2f} not within expected range (0.4-0.6)"
        )
        assert 0.7 <= height_ratio <= 1.0, (
            f"Window height ratio {height_ratio:.2f} not within expected range (0.7-1.0)"
        )
        
        self.log.info("✅ Split Screen functionality verified successfully!")

    def teardown_test(self):
        """Clean up after test."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
            self.log.info("Terminal process terminated")
        elif self.terminal_window and self.terminal_window.isActive:
            self.terminal_window.close()
            self.log.info("Terminal window closed")

    def teardown_class(self):
        """Final cleanup."""
        # Reset any system state if needed
        try:
            # Reset window manager state
            subprocess.run(["wmctrl", "-c", "Terminal"], 
                         capture_output=True, timeout=5)
        except Exception as e:
            self.log.warning(f"Could not reset window manager: {e}")


if __name__ == "__main__":
    test_runner.main()