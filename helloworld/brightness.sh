cat > check_device.sh << 'EOF'
#!/bin/bash
echo "=== Device Diagnostic ==="
echo "1. Checking ADB devices:"
adb devices
echo ""
echo "2. Checking specific device:"
adb -s emulator-5554 shell getprop ro.product.model 2>/dev/null || echo "Device not reachable"
echo ""
echo "3. Checking ADB server:"
adb start-server
echo ""
echo "4. Final device list:"
adb devices
EOF