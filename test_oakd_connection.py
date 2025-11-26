#!/usr/bin/env python3
import depthai as dai

def main():
    print("Checking for OAK-D / OAK-D Lite device...")

    try:
        device_infos = dai.Device.getAllAvailableDevices()

        if len(device_infos) == 0:
            print("❌ No OAK-D device found.")
            print("Tips:")
            print("  • Make sure the USB-C cable is data-capable (not charging-only).")
            print("  • Try a different USB port.")
            print("  • Check power supply (Pi 5 needs enough power).")
            return

        print(f"✅ Found {len(device_infos)} OAK-D device(s):")
        for info in device_infos:
            print("  • MX ID:", info.getMxId())

        # test opening a device
        print("\nTrying to connect to OAK-D...")
        with dai.Device() as device:
            print("✅ Successfully connected to OAK-D Lite!")
            print("Device name:", device.getDeviceName())
            print("USB speed:", device.getUsbSpeed())
            print("Connected cameras:", device.getConnectedCameraFeatures())

    except Exception as e:
        print("❌ Error while checking device:")
        print(e)

if __name__ == "__main__":
    main()

