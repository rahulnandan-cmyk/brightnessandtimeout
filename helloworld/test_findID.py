import subprocess
import logging

def find_system_tray_ids():
    """Find system tray and Settings IDs using xdotool."""
    try:
        # Find all windows containing "tray" or "system" in their name
        result = subprocess.run([
            'xdotool', 'search', '--name', '.*[Tt]ray.*|.*[Ss]ystem.*'
        ], capture_output=True, text=True)
        
        if result.stdout:
            window_ids = result.stdout.strip().split('\n')
            logging.info(f"Found potential system tray windows: {window_ids}")
            
            # Get detailed info about each window
            for win_id in window_ids:
                name_result = subprocess.run([
                    'xdotool', 'getwindowname', win_id
                ], capture_output=True, text=True)
                
                class_result = subprocess.run([
                    'xdotool', 'getwindowclassname', win_id
                ], capture_output=True, text=True)
                
                logging.info(f"Window {win_id}: '{name_result.stdout.strip()}' (Class: {class_result.stdout.strip()})")
        
        return window_ids
        
    except Exception as e:
        logging.error(f"Error finding system tray: {e}")
        return []

def find_settings_in_tray():
    """Find and interact with Settings in system tray."""
    try:
        # Method 1: Use xprop to find tray menu
        result = subprocess.run([
            'xprop', '-root'
        ], capture_output=True, text=True)
        
        # Look for tray-related properties
        for line in result.stdout.split('\n'):
            if 'tray' in line.lower() or 'system' in line.lower():
                logging.info(f"Tray property: {line}")
        
        # Method 2: Click coordinates and then search for menu window
        pyautogui.click(1841, 8)  # Click system tray
        time.sleep(1)
        
        # Now search for the popup menu
        menu_result = subprocess.run([
            'xdotool', 'search', '--class', '.*[Mm]enu.*|.*[Pp]opup.*'
        ], capture_output=True, text=True)
        
        if menu_result.stdout:
            menu_ids = menu_result.stdout.strip().split('\n')
            logging.info(f"Found menu windows: {menu_ids}")
            
            for menu_id in menu_ids:
                # Get all text from the menu window
                text_result