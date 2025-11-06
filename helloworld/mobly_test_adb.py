#!/usr/bin/env python3
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device

class AndroidTest(base_test.BaseTestClass):
    def setup_class(self):
        print("🚀 Setting up Android test...")
        try:
            self.ads = self.register_controller(android_device)
            self.ad = self.ads[0]
            print(f"✅ Connected to device: {self.ad.serial}")
        except Exception as e:
            print(f"❌ Failed to connect to device: {e}")
            raise

    def test_device_info(self):
        """Test basic device information"""
        print("📱 Getting device information...")

        # Use ADB commands directly for device info
        model = self.ad.adb.shell('getprop ro.product.model')
        version = self.ad.adb.shell('getprop ro.build.version.release')
        serial = self.ad.serial

        print(f"   Model: {model.strip()}")
        print(f"   Android Version: {version.strip()}")
        print(f"   Serial: {serial}")

    def test_basic_operations(self):
        """Test basic device operations"""
        print("⚡ Testing basic operations...")

        # Wake up device
        self.ad.adb.shell('input keyevent KEYCODE_WAKEUP')
        print("   Device woken up")

        # Press home to ensure we're on home screen
        self.ad.adb.shell('input keyevent KEYCODE_HOME')
        print("   Home button pressed")

        # Take a screenshot using ADB
        self.ad.adb.shell('screencap -p /sdcard/mobly_test_screenshot.png')
        print("   Screenshot taken at /sdcard/mobly_test_screenshot.png")

    def test_input_events(self):
        """Test various input events"""
        print("🎮 Testing input events...")

        # Test tap
        self.ad.adb.shell('input tap 500 500')
        print("   Tap event sent")

        # Test swipe
        self.ad.adb.shell('input swipe 300 1000 300 500 500')
        print("   Swipe event sent")

        # Go back home
        self.ad.adb.shell('input keyevent KEYCODE_HOME')
        print("   Returned to home")

    def teardown_class(self):
        """Clean up after tests"""
        # Put device to sleep
        self.ad.adb.shell('input keyevent KEYCODE_SLEEP')
        print("🎯 Test completed!")

if __name__ == '__main__':
    test_runner.main()