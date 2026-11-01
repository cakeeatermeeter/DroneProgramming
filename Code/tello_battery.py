import sys

def getBatteryValue(tello):
    batteryValue = tello.get_battery()
    print(f"Battery value: {batteryValue}%")
    batteryCheck(batteryValue, tello)

def batteryCheck(batteryValue, tello):
    if(batteryValue < 20):
        print("Battery too low for flight. Please charge the battery.")
        tello.end()
        sys.exit()