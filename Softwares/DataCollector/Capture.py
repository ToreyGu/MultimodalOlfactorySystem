'''
Descripttion: 
version: 
Author: TheiiKu
Date: 2023-06-28 15:23:49
LastEditors: TheiiKu
LastEditTime: 2023-07-03 21:47:26
afterAnnotation: CRATED IN JLU SENSOR LAB
'''
import cv2
from PyCameraList.camera_device import list_video_devices
from time import strftime , localtime , time

class Capture():
    def __init__(self):
        super(Capture, self).__init__()
        
        self.CaptureIDList              = []                    #   The available camera ID that was scanned
        self.CaptureDescriptionList     = []                    #   The available camera Description that was scanned
        self.CaptureConnectFlag         = False                 #   The Capture connect flag , 0 :No available Capture  , 1 : have available Capture

        self._Capture                   = None                  #   The camera object that collected the dataset
        self.CaptureID                  = None                  #   The selected camera ID
        self._CaptureOpenFlag           = False                 #   The video open flag , 0 close , 1 open 
        self._CaptureMirrorFlag         = 0                     #   Mirrored flag, turned on when facing the camera
        
        self.CaptureFrame               = None                  #   Buffer of video frames
        self.CaptureFrameRgb            = None                  #   Rgb frames send to QT label
        self._CapturePictureName        = None
        self._CapturePictureDir         = './picture'           #   folder where the data is stored
        self.CaptureFrameReadyFlag      = False                 #   Buffer flag bits 0：Not ready 1:ready 

        self._CaptureFps                = None
    #Scan camera information
    def getCaptureInfo(self):
        self.CaptureConnectFlag  = False
        self.CaptureIDList.clear()
        self.CaptureDescriptionList.clear()
        camLists = list_video_devices() 
        for i in range (len(camLists)):
            self.CaptureIDList.append(str(camLists[i][0]))
            self.CaptureDescriptionList.append(camLists[i][1])
        if len(self.CaptureIDList) > 0 :
            self.CaptureConnectFlag  = True
        #debug
        print('CaptureIDList' , self.CaptureIDList)
        print('CaptureDescriptionList' , self.CaptureDescriptionList)
   
    #Turn on the camera automaticly
    def openCapture(self):
        

        self._Capture = cv2.VideoCapture(self.CaptureID)
        if self._Capture.isOpened():
            self._CaptureFps = self._Capture.get(5)
            self._CaptureOpenFlag = True
            print('Capture Success')
        else : 
            self._CaptureFps = None
            self._CaptureOpenFlag = False
            print('Capture Falid')

        #debug
        
        print("openCapture(self):" )
        print("CaptureOpenFlag " ,self._CaptureOpenFlag )
        print("CaptureOpenFlag " ,self._CaptureOpenFlag )
    
    #Turn on the camera manually
    def openCaptureManual(self ,CaptureID ):
        self._Capture = cv2.VideoCapture(CaptureID)
        if self._Capture.isOpened():
            
            self._CaptureOpenFlag = True
            print('Capture Success')
        else : 
            self._CaptureOpenFlag = False
            print('Capture Falid')
        #debug
        print("openCaptureManual(self ,CaptureID ):" )
        print("CaptureOpenFlag " ,self._CaptureOpenFlag )
        
    #Turn off the camera
    def closeCapture(self ):
        self._Capture.release()
        self._CaptureOpenFlag = False
        self._CaptureFps = None
        self.CaptureFrame = None
        #debug
        print("closeCapture(self ):" )
        print("CaptureFrameReadyFlag" , self.CaptureFrameReadyFlag)

    #Get a single frame to buffer
    def getFrame(self):
        
        ret, frame  =  self._Capture.read()
        # When the flag position is 1, the image is horizontally 
        # mirrored and inverted, which is convenient for the 
        # operator to operate when facing the camera
        if self._CaptureMirrorFlag == 1:
            frame = cv2.flip(frame ,1)
        self.CaptureFrameRgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.CaptureFrame = frame
        self.CaptureFrameReadyFlag = True            
        
        #debug
        #print("getFrame(self): " )
        #print("CaptureFrameReadyFlag" , self.CaptureFrameReadyFlag)
        #cv2.imshow("debug", self.CaptureFrame)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

    #Save the selected frame
    def saveFrameFile(self):
        # Name the dataset file using system local time (Y_m_d_H_M_S)
        Localtime = strftime('%Y_%m_%d_%H_%M_%S',localtime(time()))
        filename =self._CapturePictureDir +'/'+ Localtime +'.png'
        self._CapturePictureName = Localtime +'.png'
        cv2.imwrite(filename , self.CaptureFrame)
        self.CaptureFrameReadyFlag = False
        #debug
        print("saveFrameFile(self): " )
        print("CaptureFrameReadyFlag " ,self.CaptureFrameReadyFlag )
        