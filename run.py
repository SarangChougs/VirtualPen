from classes.main import VirtualPen
import keyboard

vp = VirtualPen()
once = False
while True:
    if keyboard.is_pressed('s'):
        print("[INFO]: ------------| Starting Canvas |-------------")
        vp.startWebCam()
        vp.setBackground(vp.captureScreen())
        vp.showOutput(webCam=True)
        once = False
    elif keyboard.is_pressed('c'):
        print("[INFO]: ------------| Starting Calibration |---------------")
        print("[INFO]: Press ('s' to save value) ('q' to quit)")
        vp.caliberate()
        once = False
    elif keyboard.is_pressed('q'):
        print("[INFO]: --------------| Closing Virtual-Pen |-----------------")
        print("[INFO]: ***| THANK YOU FOR USING VIRTUAL-PEN |***")
        print("[INFO]: ***| Created by :- SarangChougs |***")
        break
    else:
        if not once:
            print("[INFO]: *****| Welcome to Virtual-Pen |*****")
            print("[INFO]: Press ('s' to Open the Canvas ) ('c' to caliberate the pointer) ('q' to quit)")
            once = True