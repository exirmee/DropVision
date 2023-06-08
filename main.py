#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import cv2
import threading
from threading import *
import time
import math
import sys
from configobj import ConfigObj
import PIL.Image, PIL.ImageTk
from PIL import Image
from PIL import ImageTk
import imutils
import numpy as np
import datetime
import csv
from tkinter import filedialog
from shutil import copyfile
import screeninfo
import random

class App():
    def __init__(self, root, window_title, video_source=0):
        #define main panel in root
        self.root = root
        self.root.overrideredirect(1)
        self.root.attributes("-topmost", True)
        #define left side panel for showing list
        self.win1 = tk.Toplevel()
        self.win1.overrideredirect(1)
        self.win1.attributes("-topmost", True)
        width = self.win1.winfo_screenwidth()
        height = self.win1.winfo_screenheight()
        self.win1.geometry('%dx%d+%d+%d' % (110, 480,width-110,0))
        #self.root.bind('<Button-1>', self.DoCalibrate)
        #self.win1.bind('<Button-1>', self.DoCalibrate)

        self.root.title(window_title)
        self.video_source = video_source
        self.analysis_switch=False
        self.show_switch=False
        self.mask_switch=False
        self.hidePanelVar=False
        self.csvList=[]



        #read configuration file
        self.config = ConfigObj('conf.cnf')

        self.delay = int(self.config["interval"])/100

        # create the main sections of the layout, and lay them out
        self.left = Frame(self.root)
        self.right = Frame(self.root)
        self.right2 = Frame(self.win1)
        self.left.pack(side=LEFT)
        self.right.pack(side=RIGHT)
        self.right2.pack(side=RIGHT)

        #Reference size  (niddle size)
        self.referenceLabel1=ttk.Label(self.root,text="Reference Size(mm)")
        self.referenceLabel1.pack(in_=self.left)
        self.reframe2=Frame(self.left)
        self.reframe2.pack()
        self.referenceVar1= tk.IntVar()
        self.referenceSlider1 = tk.Spinbox(self.reframe2, from_=0, to=5,textvariable=self.referenceVar1,width=2)
        self.referenceSlider1.pack(side=LEFT)
        self.referenceVar2= tk.IntVar()
        self.referenceSlider2 = tk.Spinbox(self.reframe2, from_=0, to=99,textvariable=self.referenceVar2,width=2)
        self.referenceSlider2.pack(side=LEFT)



        #Bulk Density value
        self.reframe1=Frame(self.left)
        self.reframe1.pack()
        self.bulkLabel=ttk.Label(self.left,text="Bulk Density(kg/m3)")
        self.bulkLabel.pack()
        self.bulkSlider = tk.Scale(self.left, from_=1, to=1500, orient="horizontal")
        self.bulkSlider.pack()

        #Drop Density value
        self.dropLabel=ttk.Label(self.left,text="Drop Density(kg/m3)")
        self.dropLabel.pack()
        self.dropSlider = tk.Scale(self.left, from_=1, to=1500, orient="horizontal")
        self.dropSlider.pack()




        #set previews values to sliders
        self.dropSlider.set(int(self.config["drop"]))
        self.bulkSlider.set(int(self.config["bulk"]))
        self.referenceVar1.set(int(self.config["niddle1"]))
        self.referenceVar2.set(int(self.config["niddle2"]))

        # tree view to show temp analisys data
        self.reframe3=Frame(self.right2)
        self.reframe3.pack()
        self.IFTvar=StringVar()
        self.list_header=['Time','IFT']
        self.tree = ttk.Treeview(self.win1,columns=self.list_header, show="headings",height=480)
        self.tree.column("Time", width=40 )
        self.tree.column("IFT", width=60)
        self.tree.heading("Time", text="Time")
        self.tree.heading("IFT", text="IFT")
        self.tree.pack()
        # creating show stream button
        self.showButton = Button(self.root, text="PlayStream",command=self.showStram,width=15, padx="2", pady="3",compound=LEFT)
        self.showButton.pack(in_=self.left)

        # creating start show expriment button
        self.satrtButton = Button(self.root,  text="Start Analysis",width=15, padx="2", pady="3",command=self.startAnalysis,compound=LEFT)
        self.satrtButton.pack(in_=self.left)

        # strat calibrating proccess (set left and right niddle coornidates)
        self.calibrateButton = Button(self.root,  text="Calibration",width=15, padx="2", pady="3",command=self.showCalibrate,compound=LEFT)
        self.calibrateButton.pack(in_=self.left)

        # show setting form
        self.settingButton = Button(self.root,  text="Setting",width=15, padx="2", pady="3",command=self.showSetting,compound=LEFT)
        self.settingButton.pack(in_=self.left)

        # creating start record expriment button to excel
        self.recButton = Button(root,  text="Export CSV",width=15, padx="2", pady="3",command=self.startRec,compound=LEFT)
        self.recButton.pack(in_=self.left)



        # creating start record expriment button to excel
        self.captureButton = Button(self.root,  text="Capture Frame",width=15, padx="2", pady="3",command=self.snapshot,compound=LEFT)
        self.captureButton.pack(in_=self.left)

        # creating reset button
        self.resetButton = Button(self.root, text="Reset List",command=self.client_reset,width=15, padx="2", pady="3",compound=LEFT)
        self.resetButton.pack(in_=self.left)

        # create show EXIT button
        self.maskButtun = Button(root,  text="Edit Mask",width=15, padx="2", pady="3",command=self.showMask,compound=LEFT)
        self.maskButtun.pack(in_=self.left)

        # create show EXIT button
        self.chartButton = Button(root,  text="Exit",width=15, padx="2", pady="3",command=self.client_exit,compound=LEFT)
        self.chartButton.pack(in_=self.left)

        #button for hide panel
        self.panelButton = Button(self.root, text="<Hide Panel",command=self.hidePanel,width=15, padx="2", pady="3")
        self.panelButton.pack(in_=self.left)

        #logo image and text
        self.logoImg = Image.open('koupal.jpg')
        self.tkimage = ImageTk.PhotoImage(self.logoImg)
        self.logoImg=tk.Label(root, image=self.tkimage,width=110,height=30)
        self.logoImg.pack(in_=self.left)
        self.logoLabel=ttk.Label(self.root,text=" شرکت تامين و توسعه \n انرژي کوپال")
        self.logoLabel.pack(in_=self.left)

        self.root.mainloop()
        
    #define a procedure to hide and show main panel
    def hidePanel(self):
        if self.hidePanelVar:
            self.referenceLabel1.pack(in_=self.left)
            self.reframe1.pack(in_=self.left)
            self.reframe2.pack(in_=self.left)
            self.dropLabel.pack(in_=self.left)
            self.dropSlider.pack(in_=self.left)
            self.bulkLabel.pack(in_=self.left)
            self.bulkSlider.pack(in_=self.left)
            self.showButton.pack(in_=self.left)
            self.satrtButton.pack(in_=self.left)
            self.calibrateButton.pack(in_=self.left)
            self.settingButton.pack(in_=self.left)
            self.recButton.pack=(self.left)
            self.captureButton.pack(in_=self.left)
            self.resetButton.pack(in_=self.left)
            self.maskButtun.pack(in_=self.left)
            self.chartButton.pack(in_=self.left)
            self.panelButton.pack(in_=self.left)

            self.panelButton.configure(text='<Hide Panel',width=15)
            self.logoImg.pack(in_=self.left)
            self.logoLabel.pack(in_=self.left)
            self.hidePanelVar=False
        else:
            self.satrtButton.pack_forget()
            self.settingButton.pack_forget()
            self.calibrateButton.pack_forget()
            self.panelButton.configure(width=1,text='>')
            self.showButton.pack_forget()
            self.recButton.pack_forget()
            self.captureButton.pack_forget()
            self.resetButton.pack_forget()
            self.maskButtun.pack_forget()
            self.chartButton.pack_forget()
            self.referenceLabel1.pack_forget()
            self.dropSlider.pack_forget()
            self.bulkSlider.pack_forget()
            self.dropLabel.pack_forget()
            self.bulkLabel.pack_forget()
            self.reframe1.pack_forget()
            self.reframe2.pack_forget()
            self.logoImg.pack_forget()
            self.logoLabel.pack_forget()
            self.hidePanelVar=True
   



    #reset p1 and p2 values and show calibrat message
    def showCalibrate(self):
        self.config["p1x"]="0"
        self.config["p2x"]="0"
        messagebox.showinfo("Calibrate", "please click at two point in picture (left and right of reference object)")
        self.config.write()
    #do the calibration each time user click at picture if p1 and p2 is  empty[0,0]
    def DoCalibrate(self,event, x, y, flags, param):
        if event==cv2.EVENT_LBUTTONDOWN:
            if self.config["p1x"]=="0":
                self.config["p1x"]=x
                self.config.write()
            elif self.config["p1x"]!="0" and self.config["p2x"]=="0":
                self.config["p2x"]=x
                self.config.write()
                messagebox.showinfo("Calibrate", "calibration compeleted!")
    def DoMask(self,event, x, y, flags, param):
        
        
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.frame,(x,y),50,(255,0,0),-1)
            cv2.circle(self.mask_img,(x,y),50,(255,0,0),-1)
            

    #show the setting modul when button clicked
    def showSetting(self):
        sett.fire()
    
    #show stream job and change button text for mask data
    def showMask(self):
        messagebox.showinfo("edit mask", "please paint in mask areas with left-click and then hit escape!")
        if self.mask_switch:
            self.mask_switch=False
            self.maskButtun["text"]="Edit Mask"

        else:
            self.mask_switch=True
            self.maskButtun["text"]="End Editing"
            self.maskShow()
 

    #show stream job and change button text
    def showStram(self):

        if self.show_switch:
            self.showButton["text"]="StartStream"
            self.show_switch=False

        else:
            self.satrtButton["text"]="Start Analysis"
            self.analysis_switch=False
            self.showButton["text"]="StopStream"
            self.show_switch=True
            showTimer=threading.Thread(target=self.updateShow)
            showTimer.start()

    #start analysis job and change button text
    def startAnalysis(self):
        if self.analysis_switch:
            self.satrtButton["text"]="Start Analysis"
            self.analysis_switch=False

        else:
            self.showButton["text"]="StartStream"
            self.show_switch=False
            self.satrtButton["text"]="Stop Analysis"
            self.analysis_switch=True
            self.updateTimer=threading.Thread(target=self.update,args=())
            self.updateTimer.start()

    # open save dialouge and save csv file
    def startRec(self):
        f =  (filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*"))))+'.csv'
        with open('.csv', 'w', newline='') as csvfile:
            fnames = ['Timer','IFT','DeMetric','DsMetric','Volume']
            writer = csv.writer(csvfile, delimiter=';',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(fnames)
            writer.writerows(self.csvList)
        copyfile('.csv', f)

    #reset everythong in form
    def client_reset(self):
        self.satrtButton["text"]="Start Analysis"
        self.analysis_switch=False
        self.show_switch=False
        self.tree.delete(*self.tree.get_children())
        self.csvList.clear()

    def client_exit(self):
        config=ConfigObj('conf.cnf')
        config['drop']=self.dropSlider.get()
        config['bulk']=self.bulkSlider.get()
        config['niddle1']=self.referenceVar1.get()
        config['niddle2']=self.referenceVar2.get()
        config.write()
        self.analysis_switch=False
        self.show_switch=False
        self.root.quit()
        self.root.destroy()
        self.win1.quit()
        self.win1.destroy()

    #capture a frame into jpeg file
    def snapshot(self):
        f =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        cv2.imwrite(f + ".jpg", self.frame)

    #get frame from video and do the analysis and return it to the monitor
    def update(self):
        #read monitor information
        screen = screeninfo.get_monitors()[0]
        width, height = screen.width, screen.height
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        cap=cv2.VideoCapture(int(config["path"])+ cv2.CAP_DSHOW)
        #start timer 
        t0 = time.time()
        while True:
            if cap.isOpened():
                # Get a frame from the video source
                ret, self.frame = cap.read()
                if ret:
                    #read frame from video and convert to gray then thresh then find edge
                    if config["Ds"]=="top":
                        self.frame = cv2.flip(self.frame, 1)
                    elif  config["Ds"]=="down":
                        self.frame = cv2.flip(self.frame, 0)
                    


                    #do prosecc on  raw image frame
                    gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                    blur=cv2.GaussianBlur(gray, (7, 7), 0)
                    flag, thresh = cv2.threshold(blur,int(config["cannyth1"]),255 , cv2.THRESH_BINARY)
                    edged=cv2.Canny(thresh,50,100)
                    edged = cv2.dilate(edged, None, iterations=1)
                    edged = cv2.erode(edged, None, iterations=1)

                    #define niddle ratio
                    distance=abs(int(config["p1x"])-int(config["p2x"]))
                    niddleVar=float(str(self.referenceVar1.get())+'.'+str(self.referenceVar2.get()))
                    ratio=float(distance)/float((niddleVar))
                    


                    
                    #define font style
                    font=cv2.FONT_HERSHEY_PLAIN

                    #ماسک کردن دایره در تصویر جهت محاسبه دقیقتر
                    circle_img = cv2.imread('mask.jpg')
                    circle_img = cv2.cvtColor(circle_img, cv2.COLOR_BGR2GRAY)
                    
                    
                    masked_data = cv2.bitwise_and(edged, edged, mask=circle_img)
                    
                    #find contours in edged capture, then grab the largest one
                    contours,hierarchy = cv2.findContours(masked_data.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

                    #find biggest countour based on area
                    if contours:
                        c=max(contours,key=cv2.contourArea)
                        
                        

                        #کشیدن ماسک محدوده اندازه گیری
                        mask_contours,mask_hierarchy = cv2.findContours(circle_img.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                        mask_c=max(mask_contours,key=cv2.contourArea)
                        cv2.drawContours(self.frame, [mask_c], -1, (255, 0, 0), 1)
                        
                        
                        # کشیدن خط دور قطره
                        cv2.drawContours(self.frame, [c], 0, (0,255,0), 1)
                        
                        #کشیدن خط سوزن
                        cv2.line(self.frame, (int(config["p1x"]),0), (int(config["p1x"]),height), (10, 120, 12), 1)
                        cv2.line(self.frame, (int(config["p2x"]),0), (int(config["p2x"]),height), (10, 120, 12), 1)

                        # determine the most extreme points along the contour
                        deRight = tuple(c[c[:, :, 0].argmax()][0])
                        deLeftTemp = tuple(c[c[:, :, 0].argmin()][0])
                        deLeft = (deLeftTemp[0],deRight[1])
                        deMid=int(round((deRight[0]+deLeft[0])/2))
                        deDownTemp = tuple(c[c[:, :, 1].argmax()][0])
                        deUpTemp = tuple(c[c[:, :, 1].argmin()][0])
                        deDown= (deMid,deDownTemp[1])
                        deTopTemp=abs(abs(deDown[1])-abs(deLeft[0]-deRight[0]))
                        deTop= (deDown[0],deTopTemp)
                        # dsTemp is the coornidates of countour that is same as deTop
                        dsTemp=c[np.where(c[:,:,:]==deTop[1]), 0 ][0]

                        #define ds and de
                        DsMetric=0.0
                        DeMetric=0.0
                        #print('deTop = ',deUpTemp)
                        #print('deDown = ',deDownTemp)

                        # Draw the contours on a seperate image
                        contours_only = np.zeros_like(self.frame)
                        cv2.drawContours(contours_only, [c], 0, (0,255,0), 1)
                        
                        gray2 = cv2.cvtColor(contours_only, cv2.COLOR_BGR2GRAY)
                        start, end = [], []
                        # Iterate through each row in the image
                        widthRow=0
                        pixelW=(1/ratio)

                        for row_num in range(gray2.shape[0]-1):
                            # Slice a row from the image
                            row = gray2[row_num: row_num + 1, :]
                            # Find the left side
                            left_px = np.argmax(row)
                            # Find the right side
                            row = np.flip(row)
                            right_px = gray2.shape[1] - np.argmax(row)
                            # Draw some of the rows
                            
                            if  left_px != 0 and right_px != 0 :
                                cv2.line(self.frame, (left_px, row_num), (right_px, row_num), (random.randrange(0, 255),random.randrange(0, 255),random.randrange(0, 255)), 2)
                                widthRow=widthRow+((abs(right_px-left_px)/ratio)*pixelW)
                                #print('width = ',(abs(right_px-left_px)/ratio)*pixelW)
                        print('--------------------------------')
                        print('ratio  = ',ratio)
                        #print('Area  = ',cv2.contourArea(c)/ratio)
                        print('widthrow = ',widthRow,' mm2')
                        vol=(pixelW)*math.pi*((widthRow/2)**2)
                        print('V = ',vol,' µl')
                        print('pixelW = ',pixelW,' mm')
                        
                   
                    
                        #
                        # if dsTemp has coornidates then grab most left and most right and put it to dsLeft,dsRight
                        if dsTemp.size:
                            dsLeft=(np.amax(dsTemp[:,0]),deTop[1])
                            dsRight=(np.amin(dsTemp[:,0]),deTop[1])
                            # put circles and coordinates of dsLeft and dsRight in screen
                            cv2.circle(self.frame, dsLeft, 5, (0, 255, 12), -1)
                            cv2.circle(self.frame, dsRight, 5, (0, 255, 12), -1)
                            #calculate distance bitween Dsleft and dsright points
                            DsPixel = np.sqrt( (dsRight[0] - dsLeft[0])**2 + (dsRight[1] - dsLeft[1])**2 )
                            DsMetric=DsPixel/ratio

                        # put circles and coordinates of deLeft and deRight and deTop and deDown in screen
                        cv2.circle(self.frame, deLeft, 5, (0, 0, 255), -1)
                        cv2.circle(self.frame, deRight, 5, (0, 0, 255), -1)
                        cv2.circle(self.frame, deTop, 5, (0, 0, 255), -1)
                        cv2.circle(self.frame, deDown, 5, (0, 0, 255), -1)
       
                        #calculate distance bitween Deleft and deright points
                        DePixel = np.sqrt( (deRight[0] - deLeft[0])**2 + (deRight[1] - deLeft[1])**2 )
                        DeMetric=DePixel/ratio


                        #calculate S
                        S=DsMetric/DeMetric
                        H=0
                        if S>0:
                            #calculat H
                            H=0.3168*S**(-2.612)

                        #calculate IFT
                        delta=abs((float(self.bulkSlider.get()))-(float(self.dropSlider.get())))
                        IFT=0
                        if H>0:
                            IFT=((delta*9.8*(DeMetric**2))*H)/1000

                        # print de and ds and S values in image
                        if S>0 and H>0 and IFT>0:
                            t1 = time.time()
                            totalTime ="{:.2f}".format(t1-t0)

                            print(totalTime)
                            cv2.rectangle(self.frame,(10,420),(630,470),(10,160,52),-1)
                            cv2.putText(self.frame,"Time="+str(datetime.datetime.now().time().strftime('%H:%M:%S')),(10,440), font, 1.5, (150,20,100),1, cv2.LINE_AA)
                            cv2.putText(self.frame,"IFT="+str(IFT),(10,460), font, 1.5, (200,0,0),1, cv2.LINE_AA)
                            self.tree.insert("" , 0, values=(str(datetime.datetime.now().time().strftime('%M:%S')),str(IFT)))
                            self.csvList.append([str(totalTime),str(IFT),str(DeMetric),str(DsMetric),str(vol)])
         
                            #['Timer','IFT','DeMetric','DsMetric','Volume']


                    #show frame in main window
                    cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
                    cv2.moveWindow('frame', screen.x - 1, screen.y - 1)
                    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                    cv2.setMouseCallback("frame", self.DoCalibrate)
                    cv2.imshow('frame',self.frame)
                    cv2.waitKey(5)

                    if self.analysis_switch==False:
                        cap.release()
                        cv2.destroyWindow('frame')
                        ConfigObj.clear(config)
                        return False

                else:
                    raise ValueError("Unable to open video source",ret)
            time.sleep(self.delay)

        #clear the config object
        ConfigObj.clear(config)
        cap.release()
    def updateShow(self):

        #read monitor information
        screen = screeninfo.get_monitors()[0]
        width, height = screen.width, screen.height
        print(width, height)
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')

        # Get a frame from the video source
        cap=cv2.VideoCapture(int(config["path"])+ cv2.CAP_DSHOW)
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)

        while self.show_switch==True:
            try:
                #read the frame from cap
                ret, frame = cap.read()
                #flip frame by the niddle sittulation
                if config["Ds"]=="top":
                    self.frame = cv2.flip(frame, 1)
                elif  config["Ds"]=="down":
                    self.frame = cv2.flip(frame, 0)
 
                #کشیدن ماسک محدوده اندازه گیری
                circle_img = cv2.imread('mask.jpg')
                circle_img = cv2.cvtColor(circle_img, cv2.COLOR_BGR2GRAY)
                mask_contours,mask_hierarchy = cv2.findContours(circle_img.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                mask_c=max(mask_contours,key=cv2.contourArea)
                cv2.drawContours(self.frame, [mask_c], -1, (0, 255, 0), 1)

                #کشیدن خط سوزن
                cv2.line(self.frame, (int(config["p1x"]),0), (int(config["p1x"]),height), (10, 120, 12), 1)
                cv2.line(self.frame, (int(config["p2x"]),0), (int(config["p2x"]),height), (10, 120, 12), 1)

                #show frame in main window
                cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
                cv2.moveWindow('frame', screen.x - 1, screen.y - 1)
                cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.setMouseCallback("frame", self.DoCalibrate)
                cv2.imshow('frame',self.frame)
                cv2.waitKey(5)

            except:
                print('gap error',ret)
            time.sleep(0.0416666666666667)

        cap.release()

        cv2.destroyWindow('frame')
        #clear the config object
        ConfigObj.clear(config)
    
    def maskShow(self):
           
        #read monitor information
        screen = screeninfo.get_monitors()[0]
        width, height = screen.width, screen.height

        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')

        # Get a frame from the video source
        cap=cv2.VideoCapture(int(config["path"])+ cv2.CAP_DSHOW)
        
        self.mask_img = np.zeros((int(cap.get(4)),int(cap.get(3))), np.uint8)

        
        while(self.mask_switch): 
            #show frame in main window
            #read the frame from cap
            ret, frame = cap.read()
            #flip frame by the niddle sittulation
            if config["Ds"]=="top":
                self.frame = cv2.flip(frame, 1)
            elif  config["Ds"]=="down":
                self.frame = cv2.flip(frame, 0)
            
            # Make sure images got an alpha channel
            
          

            
            cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow('frame', screen.x - 1, screen.y - 1)
            cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.setMouseCallback("frame", self.DoMask)
            # Add the images 
            image1=cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            
            
            img = cv2.addWeighted(image1, 0.5, self.mask_img, 0.5, 0.0) 
            
            cv2.imshow('frame',img)
            cv2.waitKey(5)
            if cv2.waitKey(20) & 0xFF == 27:
                cv2.imwrite( "mask.jpg", self.mask_img)
                cv2.destroyWindow('frame')
                self.mask_switch=False
                self.maskButtun["text"]="Edit Mask"
                break

        #clear the config object
        ConfigObj.clear(config)
class sett():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        self.window.geometry('%dx%d+%d+%d' % (150, 480,width/2-90,0))

        # create the main sections of the layout,
        # and lay them out
        self.left = Frame(window)
        self.right = Frame(window)
        self.left.pack(side=LEFT)
        self.right.pack(side=RIGHT)

        #combobox widget for video input
        self.lblCam=tk.Label(window,text="Camera Number")
        self.lblCam.pack(in_=self.right)
        self.CamCombo=ttk.Combobox(window,value=['0', '1','2', '3'])
        self.CamCombo.pack(in_=self.right)

       #scale widget for canny edge threshold
        self.lbl1=tk.Label(window,text="Threshold")
        self.lbl1.pack(in_=self.right)
        self.thSlider = tk.Scale(window, from_=0, to=255, orient="horizontal")
        self.thSlider.pack(in_=self.right)

        #scale widget for brightness
        self.lbl3=tk.Label(window,text="brightness")
        self.lbl3.pack(in_=self.right)
        self.brightslider = tk.Scale(window, from_=0, to=255, orient="horizontal")
        self.brightslider.pack(in_=self.right)

        #scale widget for Analysis Speed in second
        self.lbl4=tk.Label(window,text="Analysis Speed(ms)")
        self.lbl4.pack(in_=self.right)
        self.SpeedText=tk.Scale(window,from_=1,to=500,orient="horizontal")
        self.SpeedText.pack(in_=self.right)

        #chekbox widget for niddle is top or down
        self.lbl3=tk.Label(window,text="Niddle Position")
        self.lbl3.pack(in_=self.right)
        self.dsCombo=ttk.Combobox(window, state="readonly",value=['top', 'down'])
        self.dsCombo.pack(in_=self.right)



        #submit button for changes
        self.btnSave=tk.Button(window,text="save changes!",command=self._do_config)
        self.btnSave.pack(in_=self.right)


        #preview button
        self.btnPre=tk.Button(window,text="exit!",command=self.client_exit,width=15)
        self.btnPre.pack(in_=self.right)


        self.config=ConfigObj('conf.cnf')
        #set config values from file to widgets
        self.CamCombo.set(self.config["path"])
        self.thSlider.set(self.config["cannyth1"])
        self.brightslider.set(self.config["bright"])
        self.dsCombo.set(self.config["Ds"])
        self.SpeedText.set(self.config["interval"])


        self.window.mainloop()

    def client_exit(self):
        self.window.quit()
        self.window.destroy()


    def _do_config(self):
        config=ConfigObj('conf.cnf')
        config['path']=self.CamCombo.get()
        config['cannyth1']=self.thSlider.get()
        config['bright']=self.brightslider.get()
        config['Ds']=self.dsCombo.get()
        config['interval']=self.SpeedText.get()
        config.write()
    def fire():
        sett(tk.Tk(), "setting")

# Create a window and pass it to the Application object
App(tk.Tk(), "DropVision Main")
