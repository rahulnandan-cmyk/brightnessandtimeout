import time
import pyautogui
import logging
from mobly import base_test, test_runner, asserts

class SleepWakeTest(base_test.BaseTestClass):
    """Suspend/Lock device using UI only (PyAutoGUI)"""

    def setup_class(self):
        # Initialize the parent class properly
        pyautogui.FAILSAFE = True
        # Use standard logging in setup_class
        logging.info("PyAutoGUI failsafe enabled")
        time.sleep(1)

    def test_sleep_wake_gui(self):
        # Use standard logging instead of self.log
        logging.info("Setup: PyAutoGUI failsafe enabled")
        
        logging.info("1. Moving to system tray")
        pyautogui.moveTo(1841, 8, duration=0.5)
        pyautogui.click()
        logging.info("Clicked system tray")
        time.sleep(2)  # wait for tray menu to appear

        logging.info("2. Clicking Lock button")
        pyautogui.moveTo(1639, 396, duration=0.5)
        pyautogui.click()
        logging.info("Clicked Lock button")
        time.sleep(5)  # give time for device to lock/sleep

        logging.info("3. Waking device by pressing shift")
        pyautogui.press('shift')
        time.sleep(2)

        logging.info("4. Verifying responsiveness")
        try:
            pos = pyautogui.position()
            logging.info(f"Device is responsive. Mouse at {pos}")
        except Exception as e:
            logging.error(f"Device is NOT responsive after wake: {e}")
            asserts.fail(f"Device failed to wake properly: {e}")

if __name__ == "__main__":
    test_runner.main()