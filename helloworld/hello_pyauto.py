import pyautogui

# print(pyautogui.displayMousePosition())
x, y = pyautogui.position()
print(f"Current mouse position: X={x}, Y={y}")
