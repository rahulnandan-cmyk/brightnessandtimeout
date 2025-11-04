#!/usr/bin/env python3
"""Simple test runner to execute both tests and merge current logs only (with live output)"""
import glob
import os
import subprocess
import sys
import time
from datetime import datetime


def main():
    """Main function to run all tests and merge logs"""
    config_file = "brightnessandtimeout.yaml"

    # Define test files
    test_files = ["src/test_timeout.py",
                  "src/test_brightness_adb.py"]

    # Timestamp for this session
    start_time = datetime.now()
    print(f"Starting Display Settings Test Suite at {start_time.strftime('%H:%M:%S')}")
    print(f"Current working directory: {os.getcwd()}")

    # Store logs created during this session
    session_logs = []

    # Run all tests sequentially
    for test_file in test_files:
        print(f"\n==========> Running: {test_file} <==========")
        print(f"Executing command: {sys.executable} {test_file} -c {config_file}")

        # Get list of existing logs before running the test
        existing_logs = set(
            glob.glob("**/display_brightness_test_*.log", recursive=True) +
            glob.glob("**/screen_timeout_test_*.log", recursive=True)
        )

        # Run the test with real-time output streaming
        process = subprocess.Popen(
            [sys.executable, test_file, "-c", config_file],
            stdout=sys.stdout,  # stream output directly to console
            stderr=sys.stderr,
        )

        # Wait for test to complete
        process.wait()

        # Track new logs created during this test (all patterns)
        current_logs = set(
            glob.glob("**/display_brightness_test_*.log", recursive=True) +
            glob.glob("**/screen_timeout_test_*.log", recursive=True)
        )
        new_logs = current_logs - existing_logs

        if new_logs:
            # Get the most recently modified log file
            latest_log = max(new_logs, key=os.path.getmtime)
            session_logs.append(latest_log)
            print(f" Log file created: {latest_log}")
        else:
            print(" No new log file created for this test")

        if process.returncode == 0:
            print(f" PASSED: {test_file}")
        else:
            print(f" FAILED: {test_file}")

        # Small delay between tests
        time.sleep(1)

    # ===== Merge logs after all tests =====
    print(f"\nMerging {len(session_logs)} log files from current session...")

    if session_logs:
        merged_log = f"merged_log_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
        with open(merged_log, "w") as outfile:
            outfile.write(
                f"TEST SESSION LOG - {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            outfile.write("=" * 60 + "\n")
            outfile.write(f"Tests run: {', '.join(test_files)}\n")
            outfile.write("=" * 60 + "\n\n")

            for log_file in session_logs:
                outfile.write(f"FILE: {log_file}\n")
                outfile.write("-" * 60 + "\n")

                try:
                    with open(log_file, "r") as infile:
                        outfile.write(infile.read())
                except FileNotFoundError:
                    outfile.write(f" Log file not found: {log_file}\n")

                outfile.write("\n" + "=" * 60 + "\n\n")

        print(f"Merged log created: {merged_log}")
        print(f"Contains logs from: {', '.join(session_logs)}")
    else:
        print("️ No log files found to merge.")

    print(f"\nTest suite completed at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
