import pyautogui

print("=== GNOME Desktop Coordinate Finder ===")
print("We'll get 3 coordinates step by step...")
print("Press Ctrl+C at any time to exit\n")

# Step 1: System Tray
print("STEP 1: Move mouse to SYSTEM TRAY (top-right corner)")
print("Press Enter when ready...")
input()
x1, y1 = pyautogui.position()
print(f"System Tray: X={x1}, Y={y1}\n")

# Step 2: Power Button  
print("STEP 2: Now click to open menu, then move to POWER OFF / LOG OUT button")
print("Press Enter when ready...")
input()
x2, y2 = pyautogui.position()
print(f"Power Button: X={x2}, Y={y2}\n")

# Step 3: Suspend Option
print("STEP 3: Now move to SUSPEND option in the power menu")
print("Press Enter when ready...")
input()
x3, y3 = pyautogui.position()
print(f"Suspend Option: X={x3}, Y={y3}\n")

print("=== ALL COORDINATES ===")
print(f"system_tray_x: {x1}")
print(f"system_tray_y: {y1}")
print(f"power_x: {x2}")
print(f"power_y: {y2}") 
print(f"suspend_x: {x3}")
print(f"suspend_y: {y3}")