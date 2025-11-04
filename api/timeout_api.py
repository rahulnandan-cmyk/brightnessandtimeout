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
                self._open_timeout_settings()

                if self.d(text=label).exists:
                    self.d(text=label).click()
                    logging.info("Selected timeout: %s", label)
                else:
                    options = [el.text for el in self.d.xpath("//*[@text]").all()]
                    logging.warning("Timeout option '%s' not found. Available: %s",
                                    label, options)
                    continue

                time.sleep(2)

                # Verify system setting is correct
                current_timeout = self._get_current_timeout()
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
                    if self._is_screen_off():
                        logging.info("Screen turned off as expected(%s)", label)
                        self._wake_up_device()
                    else:
                        logging.warning("Screen still ON after %ds (%s)", wait_sec, label)
                        error_msg = (f"Screen did not turn off after {wait_sec}s "
                                     f"for timeout {label}.")
                        asserts.fail(error_msg)
                else:
                    logging.warning("Screen-off verification skipped (wait_sec=0) for (%s)",
                                    label)
                    self.d.press("home")
                    time.sleep(2)

            except (RuntimeError, ValueError, OSError) as e:
                logging.error("Error testing timeout '%s': %s", label, e, exc_info=True)
                self.d.press("home")
                time.sleep(2)
                raise

    def verify_current_timeout(self, expected_ms: int) -> bool:
        """
        Verifies that the current timeout matches the expected value.

        Args:
            expected_ms: Expected timeout value in milliseconds

        Returns:
            bool: True if timeout matches, False otherwise
        """
        try:
            current_timeout = self._get_current_timeout()
            if current_timeout == expected_ms:
                logging.info("Timeout verified: %dms", expected_ms)
                return True
            else:
                logging.warning("Timeout mismatch: expected %dms, got %dms",
                                expected_ms, current_timeout)
                return False
        except (RuntimeError, ValueError, OSError) as e:
            logging.error("Error verifying timeout: %s", e)
            return False

    def _open_timeout_settings(self) -> None:
        """Protected method wrapper for opening timeout settings."""
        # pylint: disable=protected-access
        self.manager._open_timeout_settings()

    def _get_current_timeout(self) -> int:
        """Protected method wrapper for getting current timeout."""
        # pylint: disable=protected-access
        return self.manager._get_current_timeout()

    def _is_screen_off(self) -> bool:
        """Protected method wrapper for checking screen state."""
        # pylint: disable=protected-access
        return self.manager._is_screen_off()

    def _wake_up_device(self) -> None:
        """Protected method wrapper for waking up device."""
        # pylint: disable=protected-access
        self.manager._wake_up_device()
