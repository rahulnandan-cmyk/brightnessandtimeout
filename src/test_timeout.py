#!/usr/bin/env python3
# test_timeout.py
"""Sequential Screen Timeout Test with Mobly and Timeout Utils"""

import sys
import os
import logging

# Parent directory to Python path to find utils module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mobly import asserts, base_test, test_runner
from mobly.controllers import android_device
from utils.screen_timeout_utils import TimeoutTestManager


class ScreenTimeoutTest(base_test.BaseTestClass):
    """Test to validate sequential screen timeout settings via UI."""

    def setup_class(self):
        """Initialize device."""
        # Register Android device
        self.ads = self.register_controller(android_device)
        self.ad = self.ads[0]

        # Create timeout test manager
        self.timeout_manager = None

    def setup_test(self):
        """Initialize per-test setup."""
        # Create test manager
        self.timeout_manager = TimeoutTestManager(self.ad)

        # Setup test environment
        if not self.timeout_manager.setup_test():
            asserts.fail("Test setup failed")

    def test_sequential_timeouts(self):
        """Sequentially set and verify all timeout options."""
        logging.info("Starting sequential timeout tests")

        # Format: (label_text, expected_ms, wait_seconds, skip)
        # Set skip=True to skip that particular timeout test
        timeout_configs = [
            ("15 seconds", 15000, 20, False),      # Test with screen-off verification
            ("30 seconds", 30000, 0, True),        # SKIPPED
            ("1 minute", 60000, 0, False),         # Test without waiting
            ("2 minutes", 120000, 0, False),       # Test without waiting
            ("5 minutes", 300000, 0, False),       # Test without waiting
            ("10 minutes", 600000, 0, True),       # SKIPPED
            ("30 minutes", 1800000, 0, False),     # Test without waiting
        ]

        # Execute the timeout tests
        self.timeout_manager.test_sequential_timeouts(timeout_configs)

    def teardown_class(self):
        """Reset screen timeout to 30 seconds and return home."""
        if hasattr(self, 'timeout_manager') and self.timeout_manager:
            self.timeout_manager.teardown_test()


# ---------------- Main Runner ----------------
if __name__ == "__main__":
    test_runner.main()