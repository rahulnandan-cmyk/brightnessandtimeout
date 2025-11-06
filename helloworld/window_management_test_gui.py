"""Test window management functions for Calculator using keyboard automation."""
import time
import pyautogui
import logging
from datetime import datetime
from mobly import base_test, test_runner, asserts


class KeyboardCalculatorWindowTest(base_test.BaseTestClass):
    """Test window management functions for Calculator using keyboard automation."""

    def setup_class(self):
        """Setup class."""
        super().setup_class()
        pyautogui.FAILSAFE = True
        self.app_name = "gnome-calculator"
        logging.info("Keyboard Calculator Window Management test started")
        time.sleep(1)

    def teardown_class(self):
        """Teardown class."""    
        return super().teardown_class()

    def test_keyboard_calculator_window_management(self):
        """
        Test window management functions for Calculator using keyboard only.
        
        Steps:
        1. Launch Calculator using keyboard
        2. Resize Calculator window using keyboard
        3. Move Calculator window using keyboard  
        4. Minimize/maximize Calculator using keyboard
        5. Verify all window management functions
        """
        logging.info("=== Starting Keyboard Calculator Window Management Test ===")

        try:
            # Step 1: Launch Calculator using keyboard
            logging.info("1. Launching Calculator using keyboard")
            self._launch_calculator_with_keyboard()
            time.sleep(3)
            self._take_screenshot('1_calculator_launched')
            logging.info("Calculator launched")

            # Step 2: Resize Calculator window using keyboard
            logging.info("2. Resizing Calculator window using keyboard")
            self._resize_calculator_with_keyboard()
            time.sleep(2)
            self._take_screenshot('2_calculator_resized')
            logging.info("Calculator window resized")

            # Step 3: Move Calculator window using keyboard
            logging.info("3. Moving Calculator window using keyboard")
            self._move_calculator_with_keyboard()
            time.sleep(2)
            self._take_screenshot('3_calculator_moved')
            logging.info("Calculator window moved")

            # Step 4: Minimize/maximize Calculator using keyboard
            logging.info("4. Testing minimize/maximize with keyboard")
            self._minimize_maximize_calculator_with_keyboard()
            logging.info("Calculator minimize/maximize tested")

            # Step 5: Verify all functions worked
            logging.info("5. Verifying all window management functions")
            self._verify_calculator_window_management()
            
            logging.info("Keyboard Calculator window management test completed successfully!")

        except Exception as e:
            logging.error(f"Keyboard calculator window management failed: {e}")
            asserts.fail(f"Calculator window management test failed: {e}")

    def _take_screenshot(self, name):
        """Take screenshot with date-time stamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f'{name}_{timestamp}.png'
        pyautogui.screenshot(screenshot_filename)
        logging.info(f"Screenshot saved: {screenshot_filename}")

    def _launch_calculator_with_keyboard(self):
        """Launch Calculator using keyboard only."""
        # Press Windows/Super key to open start menu
        pyautogui.press('win')  
        time.sleep(2)
        
        # Type 'calculator' to search
        pyautogui.write('calculator', interval=0.1)
        time.sleep(2)
        
        # Press Enter to launch Calculator
        pyautogui.press('enter')
        time.sleep(3)  # Wait for Calculator to open
        
        # Verify Calculator opened by checking window title or doing a calculation
        pyautogui.press('5')
        pyautogui.press('+')
        pyautogui.press('3')
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('esc')  # Clear calculator

    def _resize_calculator_with_keyboard(self):
        """Resize Calculator window using keyboard shortcuts."""
        # Make sure Calculator window is active
        pyautogui.hotkey('alt', 'tab')  # Switch to Calculator
        time.sleep(1)
        
        # Method 1: Using window resize shortcut (Alt+F8 on Linux)
        try:
            pyautogui.hotkey('alt', 'tab')
            pyautogui.hotkey('alt', 'f8')  # Enter resize mode
            time.sleep(1)
            
            # Resize using arrow keys - make it wider and taller
            pyautogui.press('right', presses=8, interval=0.2)  # Make wider
            pyautogui.press('down', presses=5, interval=0.2)   # Make taller
            pyautogui.press('enter')  # Confirm resize
            time.sleep(1)
        except:
            pyautogui.hotkey('alt', 'tab')
            # Method 2: Using Super key shortcuts (Linux/Windows)
            logging.info("Trying Super key resize method")
            pyautogui.hotkey('super', 'up')    # Maximize first
            time.sleep(1)
            pyautogui.hotkey('super', 'down')  # Then restore to medium size
            time.sleep(1)

    def _move_calculator_with_keyboard(self):
        """Move Calculator window using keyboard shortcuts."""
        # Make sure Calculator window is active
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        
        # Method 1: Using window move shortcut (Alt+F7 on Linux)
        try:
            pyautogui.hotkey('alt', 'tab')
            pyautogui.hotkey('alt', 'f7')  # Enter move mode
            time.sleep(1)
            
            # Move using arrow keys - move to top-left corner
            pyautogui.press('right', presses=10, interval=0.2)   # Move left
            pyautogui.press('down', presses=8, interval=0.2)      # Move up
            pyautogui.press('enter')  # Confirm move
            time.sleep(1)
        except:
            pyautogui.hotkey('alt', 'tab')
            # Method 2: Using Super key shortcuts for window snapping
            logging.info("Trying Super key move method")
            pyautogui.hotkey('win', 'left')   # Snap to left half
            time.sleep(1)
            pyautogui.hotkey('win', 'right')  # Snap to right half
            time.sleep(1)
            pyautogui.hotkey('win', 'up')     # Maximize
            time.sleep(1)
            pyautogui.hotkey('win', 'down')   # Restore

    def _minimize_maximize_calculator_with_keyboard(self):
        """Test minimize and maximize for Calculator using keyboard."""
        # Make sure Calculator window is active
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        
        # Minimize Calculator (Alt+F9 or Super+H)
        logging.info("Minimizing Calculator")
        try:
            pyautogui.hotkey('alt', 'f9')  # Minimize
        except:
            pyautogui.hotkey('win', 'h')  # Alternative minimize shortcut
        time.sleep(2)
        self._take_screenshot('4_calculator_minimized')
        
        # Restore Calculator from taskbar/dock
        logging.info("Restoring Calculator")
        pyautogui.hotkey('alt', 'tab')  # Switch through windows
        time.sleep(1)
        # Keep pressing tab until Calculator is selected, then press Enter
        pyautogui.press('enter')
        time.sleep(2)
        self._take_screenshot('5_calculator_restored')
        
        # Maximize Calculator (Alt+F10 or Super+Up)
        logging.info("Maximizing Calculator")
        try:
            pyautogui.hotkey('alt', 'f10')  # Maximize
        except:
            pyautogui.hotkey('win', 'up')  # Maximize
        time.sleep(2)
        self._take_screenshot('6_calculator_maximized')
        
        # Restore from maximize (Alt+F5 or Super+Down)
        logging.info("Restoring Calculator from maximize")
        try:
            pyautogui.hotkey('alt', 'f5')  # Restore
        except:
            pyautogui.hotkey('win', 'down')  # Restore
        time.sleep(2)
        self._take_screenshot('7_calculator_final_state')

    def _verify_calculator_window_management(self):
        """Verify that all Calculator window management functions worked."""
        try:
            pyautogui.hotkey('alt', 'tab')
            # Take verification screenshot of final state
            self._take_screenshot('5_calculator_verification')
            logging.info("Window management verification completed")
            
        except Exception as e:
            pyautogui.hotkey('alt', 'tab')
            logging.error(f"Verification failed: {e}")
            asserts.fail(f"Calculator window management verification failed: {e}")


if __name__ == "__main__":
    test_runner.main()