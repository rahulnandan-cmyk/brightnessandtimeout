import pyautogui
import subprocess
import time

# Add a small pause after each action for safety
pyautogui.PAUSE = 0.5

print("Launching gedit...")

# Step 1: Launch gedit
subprocess.Popen(["gedit"])
time.sleep(2.5)  # give it time to open

# Step 2: Type some text
pyautogui.typewrite("Hello Rahul 👋", interval=0.1)
pyautogui.press('enter')
pyautogui.typewrite("This file was typed and saved automatically using PyAutoGUI!", interval=0.1)

# Step 3: Save file (Ctrl+S)
pyautogui.hotkey('ctrl', 's')
time.sleep(1)

# Step 4: Type filename and press Enter
pyautogui.typewrite('pyautogui_demo1.txt', interval=0.1)
pyautogui.press('enter')

# Optional: Wait for save to complete
time.sleep(1)

# Step 5: Close gedit (Ctrl+Q)
pyautogui.hotkey('ctrl', 'q')

print("✅ File saved and gedit closed successfully.")
