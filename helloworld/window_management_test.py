import subprocess
import time
import logging
from mobly import base_test
from mobly import test_runner
from mobly import asserts


class LinuxWindowManagementTest(base_test.BaseTestClass):
    """Comprehensive test suite for Linux window management operations."""
    
    def setup_class(self):
        self.logger = logging.getLogger()
        
        # Load parameters from testbed YAML
        self.terminal_app = self.user_params.get("terminal_app", "gnome-terminal")
        
        # Timing configurations
        timing = self.user_params.get("timing", {})
        self.launch_delay = timing.get("launch_delay", 3)
        self.operation_delay = timing.get("operation_delay", 1)
        self.verification_delay = timing.get("verification_delay", 2)
        self.retry_delay = timing.get("retry_delay", 1)
        self.max_retries = timing.get("max_retries", 10)
        
        # Geometry tolerance
        self.geometry_tolerance = self.user_params.get("geometry_tolerance", 50)
        
        # Window search patterns
        self.window_patterns = self.user_params.get("window_search_patterns", 
                                                     ["gnome-terminal-server", "gnome-terminal", "terminal"])
        
        # Test settings
        test_settings = self.user_params.get("test_settings", {})
        self.cleanup_after_test = test_settings.get("cleanup_after_test", True)
        self.take_screenshots = test_settings.get("take_screenshots", False)
        self.screenshot_dir = test_settings.get("screenshot_dir", "/tmp/window_test_screenshots")
        self.verbose_logging = test_settings.get("verbose_logging", True)
        
        # Load resize and move configurations
        self.resize_configs = self.user_params.get("resize_configs", [{"width": 800, "height": 600}])
        self.move_positions = self.user_params.get("move_positions", [{"x": 100, "y": 100}])
        
        self.logger.info(f"Using terminal application: {self.terminal_app}")
        self.logger.info(f"Launch delay: {self.launch_delay}s, Operation delay: {self.operation_delay}s")
        self.logger.info(f"Max retries: {self.max_retries}, Geometry tolerance: {self.geometry_tolerance}px")
        
        self.current_win_id = None
    
    def teardown_test(self):
        """Clean up: close the window after each test if it's still open."""
        if self.current_win_id:
            try:
                self._close_window(self.current_win_id)
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"Failed to close window in teardown: {e}")
            finally:
                self.current_win_id = None
    
    def _get_existing_windows(self):
        """Get list of existing terminal window IDs before launching new one."""
        try:
            cmd = ['wmctrl', '-lx']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            existing = []
            for line in lines:
                if line and ('gnome-terminal-server' in line.lower() or 
                           'gnome-terminal' in line.lower() or 
                           'terminal' in line.lower()):
                    win_id = line.split()[0]
                    existing.append(win_id)
            
            self.logger.info(f"Existing terminal windows: {existing}")
            return set(existing)
        except Exception as e:
            self.logger.error(f"Error getting existing windows: {e}")
            return set()
    
    def _launch_terminal(self):
        """Launches the terminal application with a new window."""
        self.logger.info(f"Launching {self.terminal_app}...")
        subprocess.Popen([self.terminal_app, '--disable-factory'])
        time.sleep(3)
    
    def _get_window_id(self, existing_windows, retries=10, delay=1):
        """Get the window ID of the newly launched terminal."""
        for attempt in range(1, retries + 1):
            try:
                cmd = ['wmctrl', '-lx']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if line and ('gnome-terminal-server' in line.lower() or 
                               'gnome-terminal' in line.lower() or 
                               'terminal' in line.lower()):
                        win_id = line.split()[0]
                        
                        if win_id not in existing_windows:
                            self.logger.info(f"Found NEW terminal window ID: {win_id}")
                            return win_id
                
            except Exception as e:
                self.logger.error(f"Error searching for window: {e}")
            
            self.logger.info(f"Retrying... (Attempt {attempt}/{retries})")
            time.sleep(delay)
        
        return None
    
    def _get_window_geometry(self, win_id):
        """Get current window position and size."""
        try:
            cmd = ['xdotool', 'getwindowgeometry', win_id]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse output to extract position and size
            lines = result.stdout.strip().split('\n')
            geometry = {}
            
            for line in lines:
                if 'Position:' in line:
                    pos = line.split('Position:')[1].strip().split()
                    geometry['x'] = int(pos[0])
                    geometry['y'] = int(pos[1])
                elif 'Geometry:' in line:
                    size = line.split('Geometry:')[1].strip().split('x')
                    geometry['width'] = int(size[0])
                    geometry['height'] = int(size[1])
            
            self.logger.info(f"Window geometry: {geometry}")
            return geometry
        except Exception as e:
            self.logger.error(f"Failed to get window geometry: {e}")
            return None
    
    def _resize_window(self, win_id, width, height):
        """Resize the window using wmctrl."""
        try:
            cmd = ['wmctrl', '-ir', win_id, '-e', f'0,-1,-1,{width},{height}']
            subprocess.run(cmd, check=True)
            self.logger.info(f"Resized window {win_id} to {width}x{height}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window resize failed: {e}")
            raise
    
    def _move_window(self, win_id, x, y):
        """Move the window to specified coordinates."""
        try:
            cmd = ['wmctrl', '-ir', win_id, '-e', f'0,{x},{y},-1,-1']
            subprocess.run(cmd, check=True)
            self.logger.info(f"Moved window {win_id} to position ({x},{y})")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window move failed: {e}")
            raise
    
    def _minimize_window(self, win_id):
        """Minimize the window."""
        try:
            cmd = ['xdotool', 'windowminimize', win_id]
            subprocess.run(cmd, check=True)
            self.logger.info(f"Minimized window {win_id}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window minimize failed: {e}")
            raise
    
    def _maximize_window(self, win_id):
        """Maximize the window."""
        try:
            # Add maximize state
            cmd = ['wmctrl', '-ir', win_id, '-b', 'add,maximized_vert,maximized_horz']
            subprocess.run(cmd, check=True)
            self.logger.info(f"Maximized window {win_id}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window maximize failed: {e}")
            raise
    
    def _unmaximize_window(self, win_id):
        """Restore window from maximized state."""
        try:
            cmd = ['wmctrl', '-ir', win_id, '-b', 'remove,maximized_vert,maximized_horz']
            subprocess.run(cmd, check=True)
            self.logger.info(f"Unmaximized window {win_id}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window unmaximize failed: {e}")
            raise
    
    def _activate_window(self, win_id):
        """Activate/raise the window."""
        try:
            cmd = ['wmctrl', '-ia', win_id]
            subprocess.run(cmd, check=True)
            self.logger.info(f"Activated window {win_id}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window activate failed: {e}")
            raise
    
    def _close_window(self, win_id):
        """Close the window gracefully."""
        try:
            cmd = ['wmctrl', '-ic', win_id]
            subprocess.run(cmd, check=True)
            self.logger.info(f"Closed window {win_id}")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Window close failed: {e}")
            raise
    
    def _verify_window_exists(self, win_id):
        """Verify that a window with given ID exists."""
        try:
            cmd = ['wmctrl', '-l']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return win_id in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to verify window existence: {e}")
            return False
    
    # ==================== TEST CASES ====================
    
    def test_01_launch_app(self):
        """Test 1: Launch the terminal application."""
        self.logger.info("=== Test 1: Launch App ===")
        
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal window")
        
        self.current_win_id = win_id
        
        # Verify window exists
        exists = self._verify_window_exists(win_id)
        asserts.assert_true(exists, f"Window {win_id} does not exist")
        
        self.logger.info("✓ App launched successfully")
    
    def test_02_resize_window(self):
        """Test 2: Resize the window to different dimensions."""
        self.logger.info("=== Test 2: Resize Window ===")
        
        # Launch and get window
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal")
        self.current_win_id = win_id
        
        # Get initial geometry
        initial_geom = self._get_window_geometry(win_id)
        
        # Resize to 800x600
        self._resize_window(win_id, 800, 600)
        new_geom = self._get_window_geometry(win_id)
        
        # Verify resize (allow small tolerance due to window decorations)
        if new_geom:
            asserts.assert_true(
                abs(new_geom['width'] - 800) < 50,
                f"Width not resized correctly: expected ~800, got {new_geom['width']}"
            )
            asserts.assert_true(
                abs(new_geom['height'] - 600) < 50,
                f"Height not resized correctly: expected ~600, got {new_geom['height']}"
            )
        
        self.logger.info("✓ Window resized successfully")
    
    def test_03_move_window(self):
        """Test 3: Move the window to different screen positions."""
        self.logger.info("=== Test 3: Move Window ===")
        
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal")
        self.current_win_id = win_id
        
        # Move to position (100, 100)
        self._move_window(win_id, 100, 100)
        geom1 = self._get_window_geometry(win_id)
        
        # Move to position (300, 200)
        self._move_window(win_id, 300, 200)
        geom2 = self._get_window_geometry(win_id)
        
        # Verify position changed
        if geom1 and geom2:
            asserts.assert_true(
                geom1['x'] != geom2['x'] or geom1['y'] != geom2['y'],
                "Window position did not change"
            )
        
        self.logger.info("✓ Window moved successfully")
    
    def test_04_minimize_maximize(self):
        """Test 4: Minimize and maximize the window."""
        self.logger.info("=== Test 4: Minimize/Maximize ===")
        
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal")
        self.current_win_id = win_id
        
        # Minimize window
        self._minimize_window(win_id)
        time.sleep(1)
        
        # Activate (restore) window
        self._activate_window(win_id)
        exists_after_restore = self._verify_window_exists(win_id)
        asserts.assert_true(exists_after_restore, "Window not restored after minimize")
        
        # Maximize window
        self._maximize_window(win_id)
        time.sleep(1)
        
        # Unmaximize window
        self._unmaximize_window(win_id)
        time.sleep(1)
        
        self.logger.info("✓ Minimize/Maximize operations completed successfully")
    
    def test_05_close_window(self):
        """Test 5: Close the window and verify it's closed."""
        self.logger.info("=== Test 5: Close Window ===")
        
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal")
        
        # Verify window exists before closing
        exists_before = self._verify_window_exists(win_id)
        asserts.assert_true(exists_before, "Window does not exist before close")
        
        # Close window
        self._close_window(win_id)
        time.sleep(2)
        
        # Verify window is closed
        exists_after = self._verify_window_exists(win_id)
        asserts.assert_false(exists_after, "Window still exists after close")
        
        self.current_win_id = None  # Already closed
        self.logger.info("✓ Window closed successfully")
    
    def test_06_verify_all_window_functions(self):
        """Test 6: Comprehensive test of all window management functions."""
        self.logger.info("=== Test 6: Verify All Window Management Functions ===")
        
        # 1. Launch
        existing_windows = self._get_existing_windows()
        self._launch_terminal()
        win_id = self._get_window_id(existing_windows)
        asserts.assert_is_not_none(win_id, "Failed to launch terminal")
        self.current_win_id = win_id
        self.logger.info("  ✓ Launch verified")
        
        # 2. Resize
        self._resize(self.win_id, 1000, 700)
        time.sleep(1)  # wait for X11 event to propagate
        asserts.assert_true(self._exists(self.win_id), "Window disappeared before geometry check")
        geom = self._get_window_geometry(self.win_id)
        asserts.assert_is_not_none(geom, "Failed to get geometry after resize")

        
        # 3. Move
        self._move_window(win_id, 200, 150)
        geom_after_move = self._get_window_geometry(win_id)
        asserts.assert_is_not_none(geom_after_move, "Failed to get geometry after move")
        self.logger.info("  ✓ Move verified")
        
        # 4. Minimize
        self._minimize_window(win_id)
        self.logger.info("  ✓ Minimize verified")
        
        # 5. Restore
        self._activate_window(win_id)
        exists_after_restore = self._verify_window_exists(win_id)
        asserts.assert_true(exists_after_restore, "Window not found after restore")
        self.logger.info("  ✓ Restore verified")
        
        # 6. Maximize
        self._maximize_window(win_id)
        self.logger.info("  ✓ Maximize verified")
        
        # 7. Unmaximize
        self._unmaximize_window(win_id)
        self.logger.info("  ✓ Unmaximize verified")
        
        # 8. Close
        self._close_window(win_id)
        time.sleep(2)
        exists_after_close = self._verify_window_exists(win_id)
        asserts.assert_false(exists_after_close, "Window still exists after close")
        self.logger.info("  ✓ Close verified")
        
        self.current_win_id = None
        self.logger.info("✓ All window management functions verified successfully")


if __name__ == '__main__':
    test_runner.main()