

import sys
from tkinter import messagebox
from PyQt5 import QtWidgets
from PyQt5 import QtGui 
from PyQt5 import QtCore
from PyQt5.Qt import QThread
from Datareader import Ui_MainWindow
from SerialCom import COMHost
from Capture import Capture
import numpy as np
import os
from PyQt5.QtChart import QDateTimeAxis,QValueAxis,QSplineSeries,QChart,QChartView
from PyQt5.QtCore import QDateTime,Qt,QTimer

#Capture Thread
class ThreadCapture(QThread):
        def __init__(self):
            super(ThreadCapture,self).__init__()
        def run(self):
            pass
#Sensorarray Thread
class ThreadCOMHost(QThread):
        def __init__(self):
            super(ThreadCOMHost,self).__init__()

class MyPyQT_Form(QtWidgets.QMainWindow , Ui_MainWindow ,Capture, COMHost ):
    
    def __init__(self):
        super().__init__()
        COMHost.__init__(self)
        Capture.__init__(self)
        self.setupUi(self)
        self.openFlag = True

        #The time range of the curve , unit is seconds
        self.TimeScaler = 10

        #Use multithreading to prevent blocking of sensor signals and digital video signals
        #                
        #CaptureStream Timer
        self.CaptureTimer = QtCore.QTimer(self)
        self.CaptureTimer.timeout.connect(self.PushCaptureStream) 
        #ArrayStream Timer
        self.SensorarrayTimer = QtCore.QTimer(self)
        self.SensorarrayTimer.timeout.connect(self.PushSensorarrayStream)
        
        
        self.CaptureThread = QThread()
        self.CaptureThread.started.connect(self.PushSensorarrayStream) 


        #Hide controls that do not need to be displayed
        self.ButCollect.setVisible(False) 
        self.ButMirror.setVisible(False) 
        
        #Data quantity counter
        self.Datacounter = 1

        #Initialize the modules
        self.InitChartModule()
        self.InitFileModule()

    #Initialize the chart
    def InitChartModule(self):
        
        #Declare charts
        self.chart = QChart()

        #Set the sensor array real-time curve
        self.seriesU3 = QSplineSeries()
        self.seriesU3.setName("U3 response")
        
        self.seriesU4 = QSplineSeries()
        self.seriesU4.setName("U4 response")

        self.seriesU5 = QSplineSeries()
        self.seriesU5.setName("U5 response")

        self.seriesU6 = QSplineSeries()
        self.seriesU6.setName("U6 response")

        self.seriesU7 = QSplineSeries()
        self.seriesU7.setName("U7 response")

        self.seriesU8 = QSplineSeries()
        self.seriesU8.setName("U8 response")

        #Add real-time curves to charts
        self.chart.addSeries(self.seriesU3)
        self.chart.addSeries(self.seriesU4)
        self.chart.addSeries(self.seriesU5)
        self.chart.addSeries(self.seriesU6)
        self.chart.addSeries(self.seriesU7)
        self.chart.addSeries(self.seriesU8)

        #Declare and initialize the XY axis
        self.timeaxisX = QDateTimeAxis()
        self.valueaxisY = QValueAxis()

        #Use local time as the X-axis range
        self.timeaxisX.setMin(QDateTime.currentDateTime().addSecs(-self.TimeScaler*1))
        self.timeaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
        self.valueaxisY.setMin(0)
        self.valueaxisY.setMax(3.3)

        #Sets the X-axis time format
        self.timeaxisX.setFormat("MM/dd hh:mm:ss")

        #Sets the number of horizontal and vertical axis meshes
        self.timeaxisX.setTickCount(6)
        self.valueaxisY.setTickCount(11)

        #Sets the horizontal and vertical coordinate name
        self.timeaxisX.setTitleText("Local Time (m/d h:m:s)")
        self.valueaxisY.setTitleText("Response")

        #Add axes to the chart
        self.chart.addAxis(self.timeaxisX,Qt.AlignBottom)
        self.chart.addAxis(self.valueaxisY,Qt.AlignLeft)
        
        #Associate curves to axes
        self.seriesU3.attachAxis(self.timeaxisX)
        self.seriesU3.attachAxis(self.valueaxisY)

        self.seriesU4.attachAxis(self.timeaxisX)
        self.seriesU4.attachAxis(self.valueaxisY)

        self.seriesU5.attachAxis(self.timeaxisX)
        self.seriesU5.attachAxis(self.valueaxisY)

        self.seriesU6.attachAxis(self.timeaxisX)
        self.seriesU6.attachAxis(self.valueaxisY)

        self.seriesU7.attachAxis(self.timeaxisX)
        self.seriesU7.attachAxis(self.valueaxisY)

        self.seriesU8.attachAxis(self.timeaxisX)
        self.seriesU8.attachAxis(self.valueaxisY)
        
        #set Chart
        self.ViewValue.setChart(self.chart)

    def DrawSeneorarrayChart(self):
        #Update the axis X
        localtime = QDateTime.currentDateTime()
        self.timeaxisX.setMin(QDateTime.currentDateTime().addSecs(-self.TimeScaler*1))
        self.timeaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
        
        self.seriesU3.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[0]))
        self.seriesU4.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[1]))
        self.seriesU5.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[2]))
        self.seriesU6.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[3]))
        self.seriesU7.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[4]))
        self.seriesU8.append(localtime.toMSecsSinceEpoch(),float(self._SerialBufferData[5]))

    #COM SETTINGS
    def addCOMItem(self):# add Description to combo box
        self.getCOMIofo()
        self.COMBox.addItems(self.SerialDescription)#get Description of all device connected to computer
        
        #debug 
        #print(self.SerialDescription)
        #print(self.SerialID)
        #print(self.SerialID)

    # 'Refresh COM' press events
    def refreshCOMItem(self):
        self.COMBox.clear()
        self.addCOMItem()

    #using combol box select COM
    def SetCOMnumber(self): 
        index = self.COMBox.currentIndex()#the index of option selected in app
        #Control the LCD display COM ID
        if index <= len(self.SerialID) and index > -1:
            #Check selected item is not empty
            comID = self.SerialID[index]
            if (len(comID) != 0):
                self.lcdNumberCOM.display(int(comID[0]))
                self.COMPort  = self.SerialDevices[index]
        print(self.COMPort)

    #CAM SETTINGS
    def addCaptureItem(self):
        self.getCaptureInfo()
        self.CaptureBox.addItems(self.CaptureDescriptionList)#get Description of all Capture connected to computer
        
        #debug
        #print(self.CaptureDescriptionList)
        #print(self.CaptureIDList)
    
    # 'Refresh Capture' press events
    def refreshCaptureItem(self):
        self.CaptureBox.clear()
        self.addCaptureItem()
    #using combol box select Capture
    def SetCaptureID(self):
        index = self.CaptureBox.currentIndex()#the index of option selected in app
        #Control the LCD display Capture ID
        if index <= len(self.CaptureIDList) and index > -1:
            #Check selected item is not empty
            camid = self.CaptureIDList[index]
            if (len(camid) != 0):
                self.lcdNumberCap.display(int(camid))
                self.CaptureID = int(camid)
    
    #Use the built-in timer of QT to configure multithreaded tasks
    def SetCaptureTimer(self):
            #The refresh time is dynamically matched to the camera FPS
        if self._CaptureFps:
            self.CaptureTimer.start(int(1000/self._CaptureFps)+5)
        else:
            self.CaptureTimer.start(int(30))
    def StopCaptureTimer(self):
        self.CaptureTimer.stop()

    def SetSensorarrayTimer(self):
        #It must be larger than the actual transfer interval, otherwise the thread will be blocked
        self.SensorarrayTimer.start(550)
    
    def StopSensorarrayTimer(self):
        self.SensorarrayTimer.stop()


    #Baudrate SETTING
    def SetBaudrate(self):#using combol box select Capture
        #The baud rate is a static parameter preset in the program

        #Control the LCD display budrate
        budrate = self.BaudrateBox.currentText()
        if (len(budrate) != 0 and budrate.isdigit()):#Check that the selected item is numeric and not empty
            self.lcdNumberBaudrate.display(int(budrate))
            self.Baudrate = budrate
        print(self.Baudrate)
        #debug
        #print(budrate)

    #Set the range of scan times
    def SetTimerange(self):

        timerange = self.TimerangeBox.currentText()
        self.TimeScaler = int(timerange)
        self.scalerLabel.setText('Scale: ' + timerange + ' s')
    #capture streaming 
    def PushCaptureStream(self):

        self.getFrame()
        if self.CaptureFrameReadyFlag == True   :
            CaptureImage = QtGui.QImage(self.CaptureFrameRgb.data, self.CaptureFrameRgb.shape[1], 
                                            self.CaptureFrameRgb.shape[0],self.CaptureFrameRgb.shape[1]*3,QtGui.QImage.Format_RGB888)
            self.CaptureStream.setPixmap(QtGui.QPixmap.fromImage(CaptureImage))
            self.CaptureFrameReadyFlag == False

        
    
    def PushSensorarrayStream(self):
                self.getCOMBuffer()
                print(self._SerialBufferData)
            #if (len(self._SerialBufferData) != 0 and self._SerialBufferData.isdigit()):
                self.ValueU3.setText(self._SerialBufferData[0])
                self.ValueU4.setText(self._SerialBufferData[1])
                self.ValueU5.setText(self._SerialBufferData[2])
                self.ValueU6.setText(self._SerialBufferData[3])
                self.ValueU7.setText(self._SerialBufferData[4])
                self.ValueU8.setText(self._SerialBufferData[5])
                self.HumiBar.setValue(int(self._SerialBufferData[6]))
                self.DrawSeneorarrayChart()
    #The dataset stores a path check, and a path is created if the path does not exist

    def CheckSystemPath(self):
         
         COMpath        =   self.DataDir 
         capturepath    =   self._CapturePictureDir

         if not os.path.isdir(COMpath):
            os.mkdir( COMpath)
             
         if not os.path.isdir(capturepath):
            os.mkdir(capturepath)
    

    #Initialize the file system and create only one file per opening         
    def InitFileModule(self):
        self.CheckSystemPath()

        self.setFile()
        self.setFileHead()
        
        self.labelFilename.setText("Created Data File : " + self._SerialFile )

    #Peripheral self-test procedure , returns false when the peripheral fails to start
    def CheckPeripheralParameters(self):
        if  self.CaptureID is not None      and     self.COMPort is not None     and    self.Baudrate:
            print('Parameters is Legal')
            return True
        else :
            return False
        
    #Program entry for handling peripheral errors    
    def HandlePeripheralParametersWrong(self):
        QtWidgets.QMessageBox.warning(self, "Peripheral warning", 
                                      "Unable to connect to peripheral!"+"\n"+"Check that the parameters are correct and that the signal cable is connected correctly" , 
                                      QtWidgets.QMessageBox.Cancel)
       

    #Start System
    def PushStartButton(self):
        
        if self.openFlag:
            if self.CheckPeripheralParameters():#The program runs when the peripheral is connected normally,
                                                #otherwise The program enters the alarm interface
                
                #Change the appearance of the button
                self.ButOpen.setStyleSheet('''QWidget{background-color:#66ffcc;}''')
                self.ButOpen.setText('OPEN')
                
                #Open the peripheral interface
                self.openCapture()
                self.openCOMPort()

                #Show hidden controls
                self.ButCollect.setVisible(True)
                self.ButMirror.setVisible(True)
                
                #Start multithreading to listen for peripheral signals
                self.SetSensorarrayTimer()
                self.SetCaptureTimer()
                #self.CaptureThread.start()

                #invert flag bit prevents the control from locking
                self.openFlag = False
            else :
                # peripheral alarm interface
                self.HandlePeripheralParametersWrong()
        else:
            #Change the appearance of the button
            self.ButOpen.setStyleSheet('''QWidget{background-color:#ee0000;}''')
            self.ButOpen.setText('CLOSE')

            #Close the peripheral interface    
            self.closeSerial()
            self.closeCapture()

            #hide controls
            self.ButCollect.setVisible(False)
            self.ButMirror.setVisible(False)

            #Stop multithreading to listen for peripheral signals
            self.StopCaptureTimer()
            #self.CaptureThread.quit()
            self.StopSensorarrayTimer()

            #invert flag bit prevents the control from locking
            self.openFlag = True

    #Save frame data, including gas sensor data and image data
    def saveFrameData(self):
        self.saveFrameFile()
        self.saveSerialData( self._CapturePictureName)
        self.labelSavetime.setText("Recently saved : " +self._CapturePictureName+" " +str(self.Datacounter) +" pieces of data were collected")
        self.Datacounter = self.Datacounter+1
    
    # Mirrors the camera signal and turns on when operating directly against the camera
    def PushMirrorButton(self):
        if self._CaptureMirrorFlag == 0:
            self._CaptureMirrorFlag = 1
        else :
            self._CaptureMirrorFlag = 0
            
        #debug
        print(self._CaptureMirrorFlag)
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.show()
    sys.exit(app.exec_())
