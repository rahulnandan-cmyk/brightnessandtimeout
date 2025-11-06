#!/usr/bin/env python3
"""Coordinate Finder for 1920x1080 screens"""
import subprocess

class CoordinateFinder1920x1080:
    def __init__(self, device_serial="emulator-5556"):
        self.device_serial = device_serial
        self.screen_width = 1920
        self.screen_height = 1080

    def enable_coordinate_display(self):
        """Enable coordinate display for 1920x1080 screen"""
        print(f"📱 Setting up for {self.screen_width}x{self.screen_height} screen")
        subprocess.run(f"adb -s {self.device_serial} shell settings put system pointer_location 1", shell=True)
        subprocess.run(f"adb -s {self.device_serial} shell settings put system show_touches 1", shell=True)
        print("✅ Touch coordinates enabled!")
        print("   Tap anywhere → See coordinates at top")
        print(f"   Screen range: X:0-{self.screen_width}, Y:0-{self.screen_height}")

    def find_common_coordinates(self):
        """Find coordinates for common UI elements on 1920x1080"""
        print("\n🎯 Let's map your 1920x1080 screen:")

        elements_1920x1080 = [
            ("Settings app icon", "Top or bottom row"),
            ("Display option in Settings", "Usually around middle"),
            ("Brightness slider", "Right side of screen"),
            ("Screen Timeout", "Below brightness"),
            ("Home button", "Bottom center"),
            ("Back button", "Bottom left"),
            ("Recent apps", "Bottom right")
        ]

        coordinates = {}

        for element, hint in elements_1920x1080:
            print(f"\n📍 {element}")
            print(f"   💡 Hint: {hint}")
            input("   👉 Tap on it NOW, then press Enter here...")
            coords = input("   Enter coordinates (x y): ").strip()
            coordinates[element] = coords
            print(f"   ✅ Saved: {coords}")

        return coordinates

    def suggest_common_locations(self):
        """Suggest common coordinate ranges for 1920x1080"""
        print("\n📊 Common coordinate ranges for 1920x1080:")
        common_locations = {
            "Top status bar": "0-1920, 0-100",
            "Notification panel": "Swipe from 960,50 to 960,500",
            "Navigation buttons": "Bottom 100 pixels",
            "Center of screen": "960,540",
            "Left side": "0-400, any height",
            "Right side": "1500-1920, any height",
            "Settings items": "500-800, 300-900"
        }

        for location, coords in common_locations.items():
            print(f"   {location}: {coords}")

if __name__ == "__main__":
    finder = CoordinateFinder1920x1080()

    try:
        finder.enable_coordinate_display()
        finder.suggest_common_locations()

        print("\n" + "="*60)
        coordinates = finder.find_common_coordinates()

        print("\n🎉 Coordinates found for YOUR 1920x1080 screen:")
        for element, coords in coordinates.items():
            print(f"   {element}: {coords}")

        # Save to file with screen size info
        with open('coordinates_1920x1080.txt', 'w') as f:
            f.write("# Coordinates for 1920x1080 screen\n")
            for element, coords in coordinates.items():
                f.write(f"# adb shell input tap {coords}\n")
                f.write(f"{element} = {coords}\n")

        print("\n💾 Saved to 'coordinates_1920x1080.txt'")

    finally:
        # Clean up
        subprocess.run(f"adb -s {finder.device_serial} shell settings put system pointer_location 0", shell=True)
        print("\n✅ Coordinate display disabled")