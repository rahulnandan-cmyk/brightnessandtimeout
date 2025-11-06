import pyautogui
import time

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True

# Step 1: Open the top-right system menu (click the volume/battery area)
# Adjust coordinates if needed for your screen
pyautogui.click(1900, 20)  # Example coordinates for top-right menu
time.sleep(1)

# Step 2: Locate the brightness slider
brightness_slider = pyautogui.locateOnScreen('brightness_slider.png', confidence=0.8)
if brightness_slider:
    slider_center = pyautogui.center(brightness_slider)
    pyautogui.click(slider_center)             # focus slider
    pyautogui.dragRel(50, 0, duration=0.5)    # increase brightness
else:
    print("Brightness slider not found!")
