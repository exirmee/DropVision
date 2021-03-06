import tkinter as tk
from tkinter import messagebox
from tkinter import ttk 
from tkinter import *
import cv2
import threading
from threading import *
import time
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

class App(threading.Thread):
    def __init__(self, root, window_title, video_source=0):
        self.root = root
        self.root.title(window_title)
        self.video_source = video_source
        self.analysis_switch=False
        self.show_switch=False
        self.csvList=[]
        #full screen app
        #self.root.overrideredirect(True)
        #self.root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        #self.root.focus_set()  # <-- move focus to this widget
        #self.root.bind("<Escape>", lambda e: e.widget.quit())
        #read configuration file
        self.config = ConfigObj('conf.cnf')
        
        self.delay = int(self.config["interval"])/100
   
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
        self.bulkLabel=ttk.Label(self.root,text="Bulk Density(g/cc) / 100")
        self.bulkLabel.pack(in_=self.right)
        self.bulkSlider = tk.Scale(self.root, from_=50, to=150, orient="horizontal")
        self.bulkSlider.pack(in_=self.right)

        #Drop Density value
        self.dropLabel=ttk.Label(self.root,text="Drop Density(g/cc) / 100")
        self.dropLabel.pack(in_=self.right)
        self.dropSlider = tk.Scale(self.root, from_=50, to=150, orient="horizontal")
        self.dropSlider.pack(in_=self.right)

        #Reference size  (niddle size)
        self.referenceLabel=ttk.Label(self.root,text="Reference Size(mm) / 100")
        self.referenceLabel.pack(in_=self.right)
        self.referenceSlider = tk.Scale(self.root, from_=50, to=200, orient="horizontal")
        self.referenceSlider.pack(in_=self.right)

        
        

        # creating show stream button 
        self.playIcon=PhotoImage(file="icons\\play.png")
        self.stopIcon=PhotoImage(file="icons\\stop.png")
        self.showButton = Button(self.root, text="PlayStream",image=self.playIcon,command=self.showStram,width=120, padx="2", pady="3",compound=LEFT)
        self.showButton.pack(in_=self.subtop1)
       
        # creating start show expriment button 
        self.satrtButton = Button(self.root,  text="Start Analysis",image=self.playIcon,width=120, padx="2", pady="3",command=self.startAnalysis,compound=LEFT)
        self.satrtButton.pack(in_=self.subtop1)
        
        # strat calibrating proccess (set left and right niddle coornidates)
        self.caliIcon=PhotoImage(file="icons\\calibrate.png")
        self.calibrateButton = Button(self.root,  text="Calibration",image=self.caliIcon,width=120, padx="2", pady="3",command=self.showCalibrate,compound=LEFT)
        self.calibrateButton.pack(in_=self.subtop2)

        # show setting form
        self.settIcon=PhotoImage(file="icons\\setting.png")
        self.settingButton = Button(self.root,  text="Setting",image=self.settIcon,width=120, padx="2", pady="3",command=self.showSetting,compound=LEFT)
        self.settingButton.pack(in_=self.subtop2)

        # creating start record expriment button to excel
        self.csvIcon=PhotoImage(file="icons\\cvs.png")
        self.recButton = Button(root,  text="Export CSV",image=self.csvIcon,width=120, padx="2", pady="3",command=self.startRec,compound=LEFT)
        self.recButton.pack(in_=self.subtop3)
        
        # create show chart button
        self.chartIcon=PhotoImage(file="icons\\chart.png")
        self.chartButton = Button(root,  text="Show Chart",image=self.chartIcon,width=120, padx="2", pady="3",command=self.show_chart,compound=LEFT)
        self.chartButton.pack(in_=self.subtop3)
        
        # creating start record expriment button to excel
        self.capIcon=PhotoImage(file="icons\\camera.png")
        self.captureButton = Button(self.root,  text="Capture Frame",image=self.capIcon,width=120, padx="2", pady="3",command=self.snapshot,compound=LEFT)
        self.captureButton.pack(in_=self.subtop4)

        # creating reset button 
        self.resIcon=PhotoImage(file="icons\\reset.png")
        self.resetButton = Button(self.root, text="Reset List",image=self.resIcon,command=self.client_reset,width=120, padx="2", pady="3",compound=LEFT)
        self.resetButton.pack(in_=self.subtop4)



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
        self.canvas = tk.Canvas(root, width = 530, height = 397, cursor="crosshair")
        self.canvas.pack(in_=self.left)
        
        
        # After it is called once, the update method will be automatically called every delay milliseconds
        #---------------------------------------

        
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
        sett.fire()

    #show stream job and change button text    
    def showStram(self):
        
        if self.show_switch:
            self.showButton["text"]="StartStream"
            self.showButton.configure(image=self.playIcon)
            self.show_switch=False
            
        else:
            self.showButton["text"]="StopStream"
            self.show_switch=True
            self.showButton.configure(image=self.stopIcon)
            self.showTimer=threading.Thread(target=self.updateShow,args=())
            #self.showTimer.daemon=True
            
            self.showTimer.start()

    #start analysis job and change button text    
    def startAnalysis(self):
        if self.analysis_switch:
            self.satrtButton["text"]="Start Analysis"
            self.satrtButton.configure(image=self.playIcon)
            self.analysis_switch=False
            
        else:
            self.satrtButton["text"]="Stop Analysis"
            self.satrtButton.configure(image=self.stopIcon)
            self.analysis_switch=True
            self.updateTimer=threading.Thread(target=self.update,args=())
            #self.updateTimer.daemon=True
            self.updateTimer.start()
    
    # open save dialouge and save csv file 
    def startRec(self):
        print(self.csvList)
        f =  (filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*"))))+'.csv'
        with open('.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerows(self.csvList)
        copyfile('.csv', f)

    #reset everythong in form
    def client_reset(self):
        self.satrtButton["text"]="Start Analysis"
        self.analysis_switch=False
        self.tree.delete(*self.tree.get_children())
        self.csvList.clear()
    
    #capture a frame into jpeg file
    def snapshot(self):
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        # Get a frame from the video source
        vid=cv2.VideoCapture(int(config["path"]))
        # Get a frame from the video source
        ret, frame = vid.read()
        f =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    
        if ret:
            cv2.imwrite(f + ".jpg", frame)
    
    #get frame from video and do the analysis and return it to the monitor
    def update(self):
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        cap=cv2.VideoCapture(int(config["path"]))
        while True:
            if cap.isOpened():
                print(self.delay)
                # Get a frame from the video source

                ret, frame = cap.read()
                frame = cv2.resize(frame, (530, 397)) 
                if ret:
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
                    ratio=float(distance)/float(self.referenceSlider.get())
                    #define font style
                    font=cv2.FONT_HERSHEY_PLAIN
        
                    #find contours in edged capture, then grab the largest one
                    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE,
                    cv2.CHAIN_APPROX_NONE)
                    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                    if cnts:
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
                        # dsTemp is the coornidates of countour that is same as deTop
                        dsTemp=c[np.where(c[:,:,:]==deTop[1]), 0 ][0]
        
                        #define ds and de
                        DsMetric=0.0
                        DeMetric=0.0

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
                        H=0
                        if S>0:
                            #calculat H
                            H=0.3168*S**(-2.612)
        

                        #calculate IFT 
                        delta=float(self.bulkSlider.get())-float(self.dropSlider.get())
                        IFT=0
                        if H>0:
                            IFT=0.01*((delta*9.8*(DeMetric**2))/H)

                        # print de and ds and S values in image
                        if S>0 and H>0 and IFT>0:
                            cv2.rectangle(frame,(10,420),(630,470),(10,160,52),-1)
                            cv2.putText(frame,"Time="+str(datetime.datetime.now().time().strftime('%H:%M:%S')),(10,440), font, 1.5, (150,20,100),1, cv2.LINE_AA)
                            cv2.putText(frame,"IFT="+str(IFT),(10,460), font, 1.5, (200,0,0),1, cv2.LINE_AA)
                            self.tree.insert("" , 0, values=(str(datetime.datetime.now().time().strftime('%M:%S')),str(IFT)))
                            self.csvList.append([str(datetime.datetime.now().time().strftime('%H:%M:%S')),str(IFT)])
        
                    else:
                        print('i cant detect object pls customize and define setting')
                
                    self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
                    self.canvas.bind("<Button-1>",self.DoCalibrate)
        
                    if self.analysis_switch==False:
                        return False
                        ConfigObj.clear(config)
                        cap.release()
                else:
                    raise ValueError("Unable to open video source", video_source)
            time.sleep(self.delay)
        #clear the config object
        ConfigObj.clear(config)
        cap.release()
    def updateShow(self):
        #read configuration file and put it to config array
        config = ConfigObj('conf.cnf')
        # Get a frame from the video source
        cap=cv2.VideoCapture(int(config["path"]))
        while True: 
            #if(cap.isOpened()):
                
            #read the frame from cap
            ret, frame = cap.read()
            print(frame)
            if ret:
                #flip frame by the niddle sittulation
                if config["Ds"]=="top":
                    frame = cv2.flip(frame, 1)
                elif  config["Ds"]=="down":
                    frame = cv2.flip(frame, 0) 
                
                #resize frame for raspberry pi
                frame = cv2.resize(frame, (530, 397)) 

                #show frame in main window
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
                self.canvas.bind("<Button-1>",self.DoCalibrate)
                    
            else:
                break
                raise ValueError("Unable to open video source")
           
            ret, frame = cap.read()
            if self.show_switch==False:
                    
                cap.release()
                ConfigObj.clear(config)
                return False
            time.sleep(0.1)    
        #clear the config object
        ConfigObj.clear(config)
        cap.release()
        
# Create a window and pass it to the Application object
App(tk.Tk(), "DropVision Main")