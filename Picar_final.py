#!/usr/bin/python
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
import time
import urllib2
import json
import MySQLdb
import serial
from SimpleCV import JpegStreamCamera,JpegStreamer,Camera

js =  JpegStreamer('0.0.0.0:8081',0.1)
#cam = Camera(0,{"width":320,"height":240})

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT) # 設定pin腳
GPIO.setup(18, GPIO.OUT) #
GPIO.setup(22, GPIO.OUT) #
GPIO.setup(23, GPIO.OUT) #

host = 'Ｘ.Ｘ.Ｘ.Ｘ'  # IP更改主機位置
#host = '172.20.10.2:8888'  # 更改主機位置
url = 'http://%s/iotPiCar/phpFunction/json_iot.php' % host
updateURL = 'http://%s/iotPiCar/phpFunction/update_iot.php?' % host



def carMov(flag,faceX,faceY,update='',movSet=0.5):
    ''' 函數帶入5個引數
        flag: 'u','r','d','l','s','t','web'
        faceX,faceY: 為臉部定位的x,y座標
        update: 更改資料庫的網址,預設為空值
        movSet: 馬達的步進值,預設為0.5 在car預計設定為執行秒數
        
        函數返回
        返回updatet字串,串接get參數字串
        '''
    # 判斷藍芽案的按鈕---start---
    
    if flag == 'u' or flag == 'r':  # 如果按上或右
        if flag == 'u':
            GPIO.output(17, False)
            GPIO.output(18, True)   #電流方向18->17 23->22
            GPIO.output(22, False)
            GPIO.output(23, True)
            #movSet=1;
            update += 'move=up'
            print '前進..... '+ update
        elif flag == 'r':
            GPIO.output(17, False)
            GPIO.output(18, True)
            GPIO.output(22, False)
            GPIO.output(23, False)
            #movSet=1;
            update += 'move=right'
            print '右轉..... '+ update
    elif flag == 'd' or flag == 'l':  # 按下或左
        if flag == 'd':
            GPIO.output(17, True)
            GPIO.output(18, False)
            GPIO.output(22, True)
            GPIO.output(23, False)
            update += 'move=down'
            print '後退..... '+ update
        elif flag == 'l':
            GPIO.output(17, False)
            GPIO.output(18, False)
            GPIO.output(22, False)
            GPIO.output(23, True)
            update += 'move=left'
            print '左轉..... '+ update
    elif flag =='s':
            GPIO.output(17, False)
            GPIO.output(18, False)
            GPIO.output(22, False)
            GPIO.output(23, False)
            update += 'move=stop'
            print '停車..... ' + update
   
    elif flag =='t':  #trace face
        cam = JpegStreamCamera("http://114.32.209.33:1234/?action=stream")
        #cam = JpegStreamCamera("http://172.20.10.13:8080/?action=stream")
        while True:
            img = cam.getImage()
            faces = img.findHaarFeatures('face.xml')
            if faces:
                bigFaces = faces.sortArea()[-1]
                bigFaces.draw()  #draw green line
                img.save(js)
                time.sleep(0.01)
                location = bigFaces.coordinates()
                print "偵測到臉部....x位置為:", location[0]
                print "偵測到臉部....y位置為:", location[1]
                faceX= location[0]
                faceY= location[0]
                x = location[0] - 160
                y = location[1] - 120
                print "距離x座標中心(160,120):", x
                print "距離y座標中心(160,120):", y
                break    #有抓到眼睛就跳出while
            else:
                print "沒有抓到臉部"
            # 判斷藍芽案的按鈕---end---
        update += 'move=trace&X='+str(faceX)+"&Y="+str(faceY)



    time.sleep(0.1)
    print '執行的網址: ' + update + '&WEB=0'
    return update

#------------def carMov end----------------------------

def execURL(url, feedback=False):
    ''' 函數帶入兩個引數
        url: 要執行的網址
        feedback: 是否要回傳資料庫轉json的格式,預設不回傳
        
        函數返回
        返回一個5個值的Tuple
        '''
    urlFp = urllib2.urlopen(url)  # 要求網址
    
    if feedback:
        dData = json.load(urlFp)  # 將response轉換為json
        #flag = dData['actionflag']   # 將返回的json '1'轉為True '0'轉為False
        #faceX = dData['FaceX']
        #facey = dData['Facey']
    
        print (dData['actionflag'],dData['FaceX'],dData['FaceY'],dData['isWeb'])
        return (dData['actionflag'],dData['FaceX'],dData['FaceY'],dData['isWeb'])
    urlFp.close()

#------------def execURL end----------------------------


while True:    #主程式
    
    while True:
        try:
            flag,faceX,faceY,isWeb= execURL(url, True)  # 設定變數初始值
            print 'Get DBData OK!'
            print  flag,faceX,faceY,isWeb
        except:
            print 'Get DBData failed, retry Now!'
            time.sleep(2)
        else:
            break

    ser = serial.Serial("/dev/serial0", 9600, timeout=0.5)
    command = ser.read()  # 讀取藍芽阜的值
    # command = False
    print command
    # if-判斷藍牙是否送值,有值才繼續執行藍牙操作
    if command:
        print "BT"
        print "Bluetooth command is " + command
        # 藍牙操作---start---
        execUpdateURL = carMov(command,faceX,faceY,updateURL)
        execURL(execUpdateURL)
# 藍牙操作---end---
    elif (isWeb!="0"):      #
        print 'web'
        print isWeb
        # Web操作---start---
        execUpdateURL = carMov(flag, faceX, faceY, updateURL)
        execURL(execUpdateURL)
    # Web操作---end---
    

# Trace操作---end---

    else:
        print "未連接"
        time.sleep(0.1)

GPIO.cleanup()
