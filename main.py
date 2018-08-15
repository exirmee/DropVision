import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
from tkinter import *
import cv2
import threading
import sys
from sett import sett
from sett import  ALL
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
import matplotlib.pyplot as plt

class App:
    def __init__(self, root, window_title, video_source=0):
        self.root = root
        self.root.title(window_title)
        self.video_source = video_source
        self.analysis_switch=False
        self.csvList=[]
        #read configuration file
        self.config = ConfigObj('conf.cnf')
        
        #open video source (by default this will try to open the computer webcam)
        self.vid = Do_Analysis(int(self.config["path"]))
     
        # create the main sections of the layout, and lay them out
        self.top=Frame(self.root)
        self.bottom=Frame(self.root)
        self.left = Frame(self.bottom)
        self.right = Frame(self.bottom)
        self.bottom.pack(side=BOTTOM)
        self.top.pack(side=TOP)
        self.left.pack(side=LEFT)
        self.right.pack(side=RIGHT)
        self.subtop1=Frame(self.top)
        self.subtop2=Frame(self.top)
        self.subtop3=Frame(self.top)
        self.subtop4=Frame(self.top)
        self.subtop1.pack(side=LEFT)
        self.subtop2.pack(side=LEFT)
        self.subtop3.pack(side=LEFT)
        self.subtop4.pack(side=LEFT)
        #Bulk Density value
        self.bulkVar=StringVar()
        self.bulkLabel=ttk.Label(self.root,text="Bulk Density(g/cc)")
        self.bulkLabel.pack(in_=self.right)
        self.bulkText=tk.Spinbox(self.root,width=8,textvariable=self.bulkVar, from_=0, to=1000)
        self.bulkText.pack(in_=self.right)
        self.bulkVar.set("1")

        #Drop Density value
        self.dropVar=StringVar()
        self.dropLabel=ttk.Label(self.root,text="Drop Density(g/cc)")
        self.dropLabel.pack(in_=self.right)
        self.dropText=tk.Spinbox(self.root,width=8,textvariable=self.dropVar, from_=0, to=1000)
        self.dropText.pack(in_=self.right)
        self.dropVar.set("1")

        #Reference size  (niddle size)
        self.referenceVar=StringVar()
        self.referenceLabel=ttk.Label(self.root,text="Reference Size(mm)")
        self.referenceLabel.pack(in_=self.right)
        self.referenceText=tk.Spinbox(self.root,width=8,textvariable=self.referenceVar, from_=0, to=1000)
        self.referenceText.pack(in_=self.right)
        self.referenceVar.set("1")

        # strat calibrating proccess (set left and right niddle coornidates)
        self.calibrateButton = Button(self.root,  text="Calibration",width=18, padx="2", pady="3",command=self.showCalibrate)
        self.calibrateButton.pack(in_=self.subtop1)

        # show setting form
        self.settingButton = Button(self.root,  text="Setting",width=18, padx="2", pady="3",command=self.showSetting)
        self.settingButton.pack(in_=self.subtop1)

        # creating start show expriment button 
        self.satrtButton = Button(self.root,  text="Start Analysis",width=18, padx="2", pady="3",command=self.threadCap)
        self.satrtButton.pack(in_=self.subtop2)

        # creating start record expriment button to excel
        self.recButton = Button(root,  text="Export CSV",width=18, padx="2", pady="3",command=self.startRec)
        self.recButton.pack(in_=self.subtop2)
        # 33333333333333333333333333333333
        self.chartButton = Button(root,  text="Show Chart",width=18, padx="2", pady="3",command=self.show_chart)
        self.chartButton.pack(in_=self.subtop3)
        # creating start record expriment button to excel
        self.captureButton = Button(self.root,  text="Capture Frame",width=18, padx="2", pady="3",command=self.snapshot)
        self.captureButton.pack(in_=self.subtop3)

        # creating reset button 
        self.quitButton = Button(self.root, text="Reset",command=self.client_reset,width=18, padx="2", pady="3")
        self.quitButton.pack(in_=self.subtop4)
        # creating exit button 
        self.quitButton = Button(self.root, text="Exit",command=self.client_reset,width=18, padx="2", pady="3")
        self.quitButton.pack(in_=self.subtop4)


        # tree view to show temp analisys data
        self.IFTvar=StringVar()
        self.list_header=['Time','IFT']
        self.tree = ttk.Treeview(self.root,columns=self.list_header, show="headings")
        self.tree.column("Time", width=40 )
        self.tree.column("IFT", width=60)
        self.tree.heading("Time", text="Time")
        self.tree.heading("IFT", text="IFT")
        self.tree.pack(in_=self.right)
        
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(root, width = self.vid.width, height = self.vid.height, cursor="crosshair")
        self.canvas.pack(in_=self.left)
        
        
        # After it is called once, the update method will be automatically called every delay milliseconds
        #---------------------------------------

        self.update()
        self.root.mainloop()
        self.client_reset()
    def show_chart(self):
        newdata = np.squeeze(self.csvList) # Shape is now: (10, 80)
        plt.plot(newdata) # plotting by columns
        plt.show()
    
    #reset p1 and p2 values and show calibrat message
    def showCalibrate(self):
        self.config["p1x"]="0"
        self.config["p2x"]="0"
        messagebox.showinfo("Calibrate", "please click at two point in picture (left and right of reference object)")

    #do the calibration each time user click at picture if p1 and p2 is  empty[0,0]
    def DoCalibrate(self,event):
        if self.config["p1x"]=="0":
            self.config["p1x"]=event.x
            self.config.write()
        elif self.config["p1x"]!="0" and self.config["p2x"]=="0":
            self.config["p2x"]=event.x
            self.config.write()
            messagebox.showinfo("Calibrate", "calibration compeleted!")

    #show the setting modul when button clicked
    def showSetting(self):
        if self.analysis_switch==True:
            self.satrtButton["text"]="Start Analysis"
            self.analysis_switch=False
        sett.fire()

    #start analysis job and change button text    
    def threadCap(self):
        if self.analysis_switch:
            self.satrtButton["text"]="Start Analysis"
            self.analysis_switch=False
        else:
            self.satrtButton["text"]="Stop Analysis"
            self.analysis_switch=True
            self.root.after(self.delay, self.update)

        Do_Analysis()
    
    # open save dialouge and save csv file 
    def startRec(self):
        print(self.csvList)
        f =  (filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*"))))+'.csv'
       
        
        with open(self.experimentVar.get()+'.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerows(self.csvList)

        copyfile(self.experimentVar.get()+'.csv', f)

    #reset everythong in form
    def client_reset(self):
        self.satrtButton["text"]="Start Analysis"
        self.analysis_switch=False
        self.config["p1x"]="0"
        self.config["p2x"]="0"
        self.experimentVar.set("myExpriment")
        self.tree.delete(*self.tree.get_children())
        self.csvList.clear()
    
    #capture a frame into jpeg file
    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        f =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    
        if ret:
            cv2.imwrite(f + ".jpg", frame)
    
    #get frame from video and do the analysis and return it to the monitor
    def update(self):
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        self.delay = self.config["interval"]
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        
        #read frame from video and convert to gray then thresh then find edge
        if config["Ds"]=="top":
            frame = cv2.flip(frame, 1)
        elif  config["Ds"]=="down":
            frame = cv2.flip(frame, 0) 
        
        #do prosecc on  raw image frame  
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur=cv2.GaussianBlur(gray, (7, 7), 0)
        #drop2=118 drop3=180
        flag, thresh = cv2.threshold(blur,int(config["cannyth1"]),255 , cv2.THRESH_BINARY)     
        edged=cv2.Canny(thresh,50,100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        #define niddle ratio 
        distance=abs(int(config["p1x"])-int(config["p2x"]))
        ratio=float(distance)/float(self.referenceVar.get())
        #define font style
        font=cv2.FONT_HERSHEY_PLAIN
        
        #find contours in edged capture, then grab the largest one
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE,
        cv2.CHAIN_APPROX_NONE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        c = max(cnts, key=cv2.contourArea)
        c=cnts[0]
        #cv2.drawContours(frame, [c], 0, (0,255,0), 1)
        # if the contour is not sufficiently large, ignore it
        cv2.drawContours(frame,c, 0, (0, 255, 0), 2)

        # determine the most extreme points along the contour
        deRight = tuple(c[c[:, :, 0].argmax()][0])
        deLeftTemp = tuple(c[c[:, :, 0].argmin()][0])
        deLeft = (deLeftTemp[0],deRight[1])
        deMid=int(round((deRight[0]+deLeft[0])/2))
        deDownTemp = tuple(c[c[:, :, 1].argmax()][0])
        deDown= (deMid,deDownTemp[1])
        deTopTemp=abs(abs(deDown[1])-abs(deLeft[0]-deRight[0]))
        deTop= (deDown[0],deTopTemp)
        
        #define ds and de
        DsMetric=0.0
        DeMetric=0.0
        
        # dsTemp is the coornidates of countour that is same as deTop
        dsTemp=c[np.where(c[:,:,:]==deTop[1]), 0 ][0]
    
        # if dsTemp has coornidates then grab most left and most right and put it to dsLeft,dsRight
        if dsTemp.size:
            dsLeft=(np.amax(dsTemp[:,0]),deTop[1])
            dsRight=(np.amin(dsTemp[:,0]),deTop[1])
            # put circles and coordinates of dsLeft and dsRight in screen
            cv2.circle(frame, dsLeft, 5, (0, 255, 12), -1)
            cv2.circle(frame, dsRight, 5, (0, 255, 12), -1)
            #calculate distance bitween Dsleft and dsright points
            DsPixel = np.sqrt( (dsRight[0] - dsLeft[0])**2 + (dsRight[1] - dsLeft[1])**2 )
            DsMetric=DsPixel/ratio
        
        # put circles and coordinates of deLeft and deRight and deTop and deDown in screen
        cv2.circle(frame, deLeft, 5, (0, 0, 255), -1)
        cv2.circle(frame, deRight, 5, (0, 0, 255), -1)
        cv2.circle(frame, deTop, 5, (0, 0, 255), -1)
        cv2.circle(frame, deDown, 5, (0, 0, 255), -1)
    

        #calculate distance bitween Deleft and deright points
        DePixel = np.sqrt( (deRight[0] - deLeft[0])**2 + (deRight[1] - deLeft[1])**2 )
        DeMetric=DePixel/ratio

        #calculate S
        S=DsMetric/DeMetric

        #calculat H
        H=0.3168*S**(-2.612)


        #calculate IFT 
        delta=float(int(self.bulkVar.get()))-float(int(self.dropVar.get()))
        IFT=0.01*((delta*9.8*(DeMetric**2))/H)

        # print de and ds and S values in image
        if S>0:
            cv2.rectangle(frame,(10,420),(630,470),(10,160,52),-1)
            cv2.putText(frame,"Time="+str(datetime.datetime.now().time().strftime('%H:%M:%S')),(10,440), font, 1.5, (150,20,100),1, cv2.LINE_AA)
            cv2.putText(frame,"IFT="+str(IFT),(10,460), font, 1.5, (200,0,0),1, cv2.LINE_AA)
            self.tree.insert("" , 0, values=(str(datetime.datetime.now().time().strftime('%M:%S')),str(IFT)))
            self.csvList.append([str(datetime.datetime.now().time().strftime('%H:%M:%S')),str(IFT)])
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            self.canvas.bind("<Button-1>",self.DoCalibrate)
        
        if self.analysis_switch==True:
            self.satrtButton["text"]="Stop Analysis"
            self.root.after(self.delay, self.update)
        #clear the config object
        ConfigObj.clear(config)

#get video streaming path and set the frame width and height 
class Do_Analysis:
    def __init__(self, video_source=0):
        
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        # Open the video source
        self.vid = cv2.VideoCapture(int(config["path"]))
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
 
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)/1.333
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)/1.333
    def get_frame(self):
        if self.vid.isOpened():
            #read configuration file
            ret, frame = self.vid.read()
            frame = cv2.resize(frame, (530, 397)) 
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, frame)
                config.clear()
            else:
                return (ret, None)
        else:
            return (ret, None)

        # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object
App(tk.Tk(), "DropVision Main")
