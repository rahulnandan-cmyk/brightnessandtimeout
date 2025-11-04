import uiautomator2 as u2
import time

d = u2.connect("emulator-5554")

# Open Settings
d.app_start("com.android.settings")
time.sleep(2)

# Find and click "Display"
if d(text="Display").exists:
    d(text="Display").click()
    print("✅ Opened Display settings")

# Scroll and click "Screen timeout"
if d(textContains="Screen timeout").exists:
    d(textContains="Screen timeout").click()
    print("✅ Opened Screen timeout menu")

# Select 30 seconds option if visible
if d(text="30 seconds").exists:
    d(text="30 seconds").click()
    print("✅ Selected 30 seconds timeout")

# Go back to home
d.press("home")
