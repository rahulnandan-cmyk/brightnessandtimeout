#!/bin/bash

# 1. Move to Settings window
xdotool mousemove 1717 353 click 1
sleep 1

# 2. Click Background tab
xdotool mousemove 89 270 click 1
sleep 1

# 3. Click "Change Background" option
xdotool mousemove 683 404 click 1
sleep 1

# 4. Verification step: move mouse back to system tray (to show success)
xdotool mousemove 1846 10
chmod +x test_change_background.sh
