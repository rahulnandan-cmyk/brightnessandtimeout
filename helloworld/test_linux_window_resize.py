import subprocess
import time
import pyautogui
from mobly import base_test
from mobly import test_runner

# Configure PyAutoGUI
pyautogui.FAILSAFE = True

class LinuxWindowResizeTest(base_test.BaseTestClass):
    """Test class to resize a terminal window and verify its geometry."""

    def setup_class(self):
        # Terminal app from YAML or default
        self.terminal_app = self.user_params.get("terminal_app", "gnome-terminal")
        print(f"Using terminal application: {self.terminal_app}")

        # Optional delay for GUI to load
        self.gui_load_delay = int(self.user_params.get("gui_load_delay", 3))

        self.process = None
        self.terminal_window = None

    def test_launch_and_resize_window(self):
        """Launch terminal, resize using PyAutoGUI, verify size."""
        target_width = int(self.user_params.get("target_width", 800))
        target_height = int(self.user_params.get("target_height", 600))

        # Launch terminal non-blocking
        print(f"Launching {self.terminal_app}...")
        self.process = subprocess.Popen([self.terminal_app])
        time.sleep(self.gui_load_delay)

        # Try multiple possible window titles
        possible_titles = ["Terminal", self.terminal_app]
        windows = []
        for title in possible_titles:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                break

        if not windows:
            raise AssertionError(
                f"Failed to find a terminal window with titles: {possible_titles}"
            )

        # Select first matching window
        self.terminal_window = windows[0]
        print(f"Identified window: '{self.terminal_window.title}'")

        # Activate and resize
        self.terminal_window.activate()
        time.sleep(0.5)
        self.terminal_window.resizeTo(target_width, target_height)
        time.sleep(1)

        # Verify size
        current_width = self.terminal_window.width
        current_height = self.terminal_window.height
        print(f"Window resized to: {current_width}x{current_height}")

        # Allow slight difference due to window decorations
        assert abs(current_width - target_width) < 50, (
            f"Width mismatch. Expected ~{target_width}, got {current_width}"
        )
        assert abs(current_height - target_height) < 50, (
            f"Height mismatch. Expected ~{target_height}, got {current_height}"
        )

        print(" Window resize verified successfully.")

    def teardown_test(self):
        """Close the terminal window."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
            print("Terminal process terminated successfully.")
        elif self.terminal_window and self.terminal_window.isActive:
            self.terminal_window.close()
            print("Terminal window closed via PyAutoGUI.")


if __name__ == "__main__":
    test_runner.main()
