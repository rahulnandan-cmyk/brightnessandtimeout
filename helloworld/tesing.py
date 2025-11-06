import pyautogui
import time

print("Move your mouse to the desired position. Waiting 5 seconds...")
time.sleep(10)

x, y = pyautogui.position()  # Get current cursor coordinates
print(f"Cursor is at: ({x}, {y})")