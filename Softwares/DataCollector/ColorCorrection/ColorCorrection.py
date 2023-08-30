'''
Descripttion: 
version: 
Author: TheiiKu
Date: 2023-08-30 19:15:34
LastEditors: TheiiKu
LastEditTime: 2023-08-30 19:34:04
afterAnnotation: CRATED IN JLU SENSOR LAB
'''

import cv2
import numpy as np
 
import os
 
image_path = "testPic/test.jpg"
 
img = cv2.imdecode(np.fromfile(image_path,dtype=np.uint8),-1)

height, width = img.shape[:2]  
size = (int(width*0.4), int(height*0.4))  
img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)  

cv2.imshow('img', img)
cv2.waitKey(0)
 
detector = cv2.mcc.CCheckerDetector_create()
 
detector.process(img, cv2.mcc.MCC24)
 
# cv2.mcc_CCheckerDetector.getBestColorChecker()
checker = detector.getBestColorChecker()
 
cdraw = cv2.mcc.CCheckerDraw_create(checker)
img_draw = img.copy()
cdraw.draw(img_draw)
 
cv2.imshow('img_draw', img_draw)
cv2.waitKey(0)
 
chartsRGB = checker.getChartsRGB()
 
src = chartsRGB[:,1].copy().reshape(24, 1, 3)
 
src /= 255.0
 
print(src.shape)
#model1 = cv2.ccm_ColorCorrectionModel(src, cv2.mcc.MCC24)
model1 = cv2.ccm_ColorCorrectionModel(src, cv2.ccm.COLORCHECKER_Macbeth)
#model1 = cv2.ccm_ColorCorrectionModel(src,src,cv2.ccm.COLOR_SPACE_sRGB)
model1.run()
ccm = model1.getCCM()
print("ccm ", ccm)
loss = model1.getLoss()
print("loss ", loss)
 
img_ = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_ = img_.astype(np.float64)
img_ = img_/255
calibratedImage = model1.infer(img_)
out_ = calibratedImage * 255
out_[out_ < 0] = 0
out_[out_ > 255] = 255
out_ = out_.astype(np.uint8)
 
out_img = cv2.cvtColor(out_, cv2.COLOR_RGB2BGR)
 
file, ext = os.path.splitext(image_path)
#calibratedFilePath = file + '_calibrated' + ext
# cv2.imwrite(calibratedFilePath, out_img)
#cv2.imencode(ext, out_img)[1].tofile(calibratedFilePath)
 
cv2.imshow('out_img', out_img)
cv2.waitKey(0)

cv2.destroyAllWindows()