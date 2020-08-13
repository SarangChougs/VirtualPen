import cv2
import time
import numpy as np
import keyboard
from PIL import ImageGrab

red = [0,0,255]
green = [0,255,0]
cyan = [255,255,0]
black = [0,0,0]
MAX = 2000
width = MAX
height = MAX

class VirtualPen():

    '''
    Constructor
    '''
    def __init__(self,res = "new"):
        self.resolution = res

        # change the resolution to default 
        if self.resolution == "default":
            self.width = None
            self.height = None
        else:
            self.width = width
            self.height = height

        self.background_canvas = None
        self.load_disk = True
        self.pointer_canvas = None
        self.paint_canvas = None
        self.x1,self.y1,self.x2,self.y2 = 0,0,0,0
        self.noiseth = 800
        self.frame = None
        self.available = False
        self.key = None
        self.white = "paint.jpg"
        self.color = red # line color
        self.pointer_color = green
        self.pointer_size = 4
        self.eraser_size = 20
        self.line_size = 4
        self.draw = False
        self.erase = False
        self.output = None
        self.background_canvas_name = None
        self.state = None
        
    '''
    Function to start the WebCam
    '''
    def startWebCam(self):
        print("[INFO]: Starting Webcam...")
        self.video = cv2.VideoCapture(0)

        # set resolution to max if default is not set
        if self.resolution != "default":   
            self.video.set(3,self.width)
            self.video.set(4,self.height)
            self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        available, self.frame = self.video.read()

    '''
    Function to show the output
    '''
    def showOutput(self, screen = False,webCam = False):
        print("[INFO]: Showing output window...")
        once = False
        while True:
            # Press o to reset the background
            if keyboard.is_pressed('r'):
                self.setBackground(self.captureScreen())
            else:
                self.available = webCam
                # check if video is available
                if self.available:
                    self.available, self.frame = self.video.read()
                    self.frame = cv2.flip(self.frame, 1)
                    self.capturePointer()
                    self.drawLine()
                    cv2.imshow("Output", self.output)
                    self.key = cv2.waitKey(1) & 0xFF
                    if keyboard.is_pressed('q'):
                        break
                else:
                    if not once:
                        print("[INFO]: Webcam is off...")
                        once = True
                    cv2.imshow("output", self.background_canvas)
                    self.key = cv2.waitKey(1) & 0xFF
                    if keyboard.is_pressed('q'):
                        break
        if self.available:
            self.video.release()
        cv2.destroyAllWindows()
        
    '''
    Function to detect the pen as a pointer
    '''
    def capturePointer(self):
        # if Webcam is off, just return
        if self.frame is None:
            print("[INFO]: Frame is not initialized...")
            return
        if self.load_disk:
            self.hsv_value = np.load('hsv_value.npy')
        else:
            print("[INFO]: No hsv_value found. Default value will be used.")
        
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

        # If reading from memory then load the upper and lower ranges from there
        if self.load_disk:
            lower_range = self.hsv_value[0]
            upper_range = self.hsv_value[1]
        # Otherwise define your own custom values for upper and lower range.
        else:           
            lower_range  = np.array([70, 80, 100])
            upper_range = np.array([179, 255, 255])
        
        # Create the mask
        mask = cv2.inRange(hsv, lower_range, upper_range)
        
        # Perform morphological operations to get rid of the noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE,np.ones((3,3),np.uint8))
        
        # Find Contours
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.pointer_canvas = None
        self.pointer_canvas = np.zeros_like(self.frame)
            
        # only process if contour is greater than noise threshold
        if contours and cv2.contourArea(max(contours, key = cv2.contourArea)) > self.noiseth:
            c = max(contours, key = cv2.contourArea)    
            self.x2,self.y2,w,h = cv2.boundingRect(c)
            cv2.circle(self.pointer_canvas, (self.x2,self.y2), self.pointer_size, self.pointer_color, thickness=-2)

    '''
    Function to take a screenshot of the desktop
    '''
    def captureScreen(self):
        print("[INFO]: Capturing background screen...")
        print("[INFO]: Press ('n' to capture new background) ('x' to use default) ('b' to use black background) ('f' to use webcam)")
        name = "background.jpg"
        while True:
            if keyboard.is_pressed('n'):
                image = ImageGrab.grab()
                image.save(name)
                self.background_canvas_name = "Desktop"
                return(name)
            elif keyboard.is_pressed('x'):
                self.background_canvas_name = "WhiteBoard"
                return("default")
            elif keyboard.is_pressed('b'):
                self.background_canvas_name = "BlackBoard"
                return("black")
            elif keyboard.is_pressed('f'):
                self.background_canvas_name = "Webcam"
                return("webcam")
            else:
                pass  

    '''
    Function to set the background of the canvas
    '''
    def setBackground(self, image):
        if image == "default":
            print("[INFO]: No background image provided...Setting Default image")
            self.background_canvas = cv2.imread(self.white)
            self.background_canvas = cv2.resize(self.background_canvas,(self.width,self.height))
        elif image == "black":
            print("[INFO]: Setting Background as Black...")
            self.background_canvas = np.zeros_like(self.frame)
            # self.background_canvas = cv2.resize(self.background_canvas,(self.width,self.height))
        elif image == "webcam":
            print("[INFO]: Setting Background as WebCam...")
            self.background_canvas = self.frame
        else:
            print("[INFO]: New Background image provided...")
            self.background_canvas = cv2.imread(image)
            self.background_canvas = cv2.resize(self.background_canvas,(self.width,self.height)) 

    '''
    Function to draw the line on paint canvas
    '''
    def drawLine(self):
        if self.paint_canvas is None:
            self.paint_canvas = np.zeros_like(self.frame)
        if self.x1 == 0 and self.y1 == 0:
            self.x1, self.y1 = self.x2,self.y2
        else:
            if self.draw:
                self.paint_canvas = cv2.line(self.paint_canvas, (self.x1,self.y1),(self.x2,self.y2), self.color, self.line_size)
            if self.erase:
                self.paint_canvas = cv2.line(self.paint_canvas, (self.x1,self.y1),(self.x2,self.y2), self.color, self.eraser_size)
        
        # after the points are drawn new points become the previous points
        self.x1, self.y1 = self.x2,self.y2
        
        # extra line for making background to live feed from webcam
        if self.background_canvas_name == "Webcam":
            self.background_canvas = self.frame

        # add the 3 canvas into a single canvas
        self.output = cv2.addWeighted(self.pointer_canvas,1,self.paint_canvas,1,0)
        self.output = cv2.addWeighted(self.background_canvas,0.5,self.output,1,0)
        
        # info to be printed on the output 
        info1 = [
        ("----MENU----","", green),
		("Draw =", "d", cyan),
		("Eraser =", "e", cyan),
		("Clear =", "c", cyan),
        ("Quit =", "q", cyan),
        ("Change BG =", "r", cyan),
        ("Take ss =", "n", cyan),
        ("Default BG =", "x", cyan),
        ("Black BG =", "b", cyan),
        ("Webcam BG = ", "f", cyan),
        ("----INFO----", "", green),
        ("State =", self.state, red),
        ("BG =", self.background_canvas_name, red)
	    ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v,c)) in enumerate(info1):
            text = "{} {}".format(k, v)
            cv2.putText(self.output, text, (10, ((i * 30) + 200)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, c, 2)

        # draw on d
        if keyboard.is_pressed('d'):
            self.draw = True
            self.erase = False
            self.color = red
            self.line_size = 4
            self.pointer_size = self.line_size
            self.state = "Draw"
        # pointer on s
        if keyboard.is_pressed('s'):
            self.draw = False
            self.erase = False
            self.state = "Pointer"
            self.pointer_size = 4
        # erase on e
        if keyboard.is_pressed('e'):
            self.color = black
            self.eraser_size = 20
            self.pointer_size = self.eraser_size - 10
            self.erase = True
            self.draw = False
            self.state = "Eraser"
        # clear on c
        if keyboard.is_pressed('c'):
            self.paint_canvas = None
        
    '''
    Function to caliberate pointer
    '''
    def caliberate(self):
        # A required callback method that goes into the trackbar function.
        def nothing(x):
            pass
        # Initializing the webcam feed.
        cap = cv2.VideoCapture(0)
        cap.set(3,1280)
        cap.set(4,720)
        print("[INFO]: Starting Webcam...")
        # Create a window named trackbars.
        cv2.namedWindow("Trackbars")

        # Now create 6 trackbars that will control the lower and upper range of 
        # H,S and V channels. The Arguments are like this: Name of trackbar, 
        # window name, range,callback function. For Hue the range is 0-179 and
        # for S,V its 0-255.
        cv2.createTrackbar("Lower - H", "Trackbars", 0, 179, nothing)
        cv2.createTrackbar("Lower - S", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("Lower - V", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("Upper - H", "Trackbars", 179, 179, nothing)
        cv2.createTrackbar("Upper - S", "Trackbars", 255, 255, nothing)
        cv2.createTrackbar("Upper - V", "Trackbars", 255, 255, nothing)
        
        while True:
            # Start reading the webcam feed frame by frame.
            ret, frame = cap.read()
            if not ret:
                break
            # Flip the frame horizontally (Not required)
            frame = cv2.flip( frame, 1 ) 
            
            # Convert the BGR image to HSV image.
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Get the new values of the trackbar in real time as the user changes them
            l_h = cv2.getTrackbarPos("Lower - H", "Trackbars")
            l_s = cv2.getTrackbarPos("Lower - S", "Trackbars")
            l_v = cv2.getTrackbarPos("Lower - V", "Trackbars")
            u_h = cv2.getTrackbarPos("Upper - H", "Trackbars")
            u_s = cv2.getTrackbarPos("Upper - S", "Trackbars")
            u_v = cv2.getTrackbarPos("Upper - V", "Trackbars")
        
            # Set the lower and upper HSV range according to the value selected by the trackbar
            lower_range = np.array([l_h, l_s, l_v])
            upper_range = np.array([u_h, u_s, u_v])
            
            # Filter the image and get the binary mask, where white represents 
            # your target color
            mask = cv2.inRange(hsv, lower_range, upper_range)
        
            # You can also visualize the real part of the target color (Optional)
            res = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Converting the binary mask to 3 channel image, this is just so 
            # we can stack it with the others
            mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # stack the mask, orginal frame and the filtered result
            stacked = np.hstack((mask_3,res,frame))
            
            # Show this stacked frame at 40% of the size.
            cv2.imshow('Trackbars',cv2.resize(stacked,None,fx=0.4,fy=0.4))
            
            # If the user presses ESC then exit the program
            key = cv2.waitKey(1) & 0xFF
            if keyboard.is_pressed('q'):
                break
            
            # If the user presses `s` then print this array.
            if keyboard.is_pressed('s'):
                theArray = [[l_h,l_s,l_v],[u_h, u_s, u_v]]
                print("[INFO]: HSV value saved : " + str(theArray))
                
                # Also save this array as hsv_value.npy
                np.save('hsv_value',theArray)
                break
            
        # Release the camera & destroy the windows.    
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
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