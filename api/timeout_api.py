#!/usr/bin/env python3
"""Timeout API functions."""
import logging
import time
from typing import List, Tuple

from mobly import asserts

# Import the core manager
from utils.display_settings_manager1 import DisplaySettingsManager


class TimeoutAPI:
    """API for timeout-related test operations."""

    def __init__(self, manager: DisplaySettingsManager):
        self.manager = manager
        self.ad = manager.ad
        self.d = manager.d

    def test_sequential_timeouts(self, timeout_labels: List[Tuple[str, int, int]]):
        """
        Tests sequential timeout options (clicks UI, verify settings, check screen-off).

        Args:
            timeout_labels: List of tuples (label, expected_ms, wait_sec).
                - label: UI text to click (eg; 15 seconds)
                - expected_ms: Excepted timeout values in milliseconds.
                - wait_sec: Seconds to wait for screen-off verification (0 to skip).
        """
        for label, expected_ms, wait_sec in timeout_labels:
            logging.info("=" * 60)
            logging.info("Testing timeout option: %s", label)
            logging.info("=" * 60)

            try:
                self.manager.open_timeout_settings()

                self.manager.scroll_and_click_setting(setting_labels=[label])
                time.sleep(2)

                # Verify system setting is correct
                current_timeout = self.manager.get_current_timeout()

                if current_timeout != expected_ms:
                    logging.error("Timeout Mismatch! Expected %d, got %d",
                                  expected_ms, current_timeout)
                    error_msg = (f"Timeout set incorrect for label {label}: "
                                 f"Expected {expected_ms}ms, got {current_timeout}ms")
                    asserts.fail(error_msg)
                else:
                    logging.info("Timeout set correctly to %dms", expected_ms)

                # Verify screen-off behaviour
                if wait_sec > 0:
                    logging.info("Waiting %ds for screen-off verification...", wait_sec)
                    time.sleep(wait_sec)
                    if self.manager.is_screen_off():
                        logging.info("Screen turned off as expected(%s)", label)
                        self.manager.wake_up_device()
                    else:
                        logging.warning("Screen still ON after %ds (%s)", wait_sec, label)
                        error_msg = (f"Screen did not turn off after {wait_sec}s "
                                     f"for timeout {label}.")
                        asserts.fail(error_msg)
                else:
                    logging.warning("Screen-off verification skipped (wait_sec=0) for (%s)",
                                    label)
                    self.manager.close_settings_dialogs()
                    time.sleep(2)

            except (RuntimeError, ValueError, OSError) as e:
                logging.error("Error testing timeout '%s': %s", label, e, exc_info=True)
                self.d.press("home")
                time.sleep(2)
                raise
