import tkinter as tk
from tkinter import ttk 
from tkinter import *
import threading
import cv2
import PIL.Image, PIL.ImageTk
from PIL import Image
from PIL import ImageTk
import time
import screeninfo
from configobj import ConfigObj
from tkinter import messagebox

class App():
        def __init__(self, root, window_title, video_source=0):
            self.root = root
            self.root.overrideredirect(1)
            self.root.title(window_title)
            self.video_source = video_source
            self.show_switch=False
            self.hidePanelVar=False
            self.showButton = Button(self.root, text="PlayStream",command=self.showStram,width=15, padx="2", pady="3")
            self.calibrateButton = Button(self.root, text="Calibrate",command=self.showCalibrate,width=15, padx="2", pady="3")
            self.panelButton = Button(self.root, text="<Hide Panel",command=self.hidePanel,width=15, padx="2", pady="3")
            self.panelButton.pack()
            self.calibrateButton.pack()
            self.showButton.pack()
            #read configuration file
            self.config = ConfigObj('conf.cnf')
            self.root.mainloop()
        def hidePanel(self):
            if self.hidePanelVar:
                self.calibrateButton.configure(width=15,text='Calibrate')
                self.panelButton.configure(width=15,text='<Hide Panel')
                self.showButton.configure(width=15,text='PlayStream')
                self.hidePanelVar=False
            else:
                self.calibrateButton.configure(width=0,text='')
                self.panelButton.configure(width=1,text='>')
                self.showButton.configure(width=0,text='')
                self.hidePanelVar=True
        def showCalibrate(self):
            self.config["p1x"]="0"
            self.config["p2x"]="0"
            messagebox.showinfo("Calibrate", "please click at two point in picture (left and right of reference object)")
            
        #do the calibration each time user click at picture if p1 and p2 is  empty[0,0]
        def DoCalibrate(self,event, x, y, flags, param):
            if event==cv2.EVENT_LBUTTONDOWN:
                print(x)
                if self.config["p1x"]=="0" :
                    self.config["p1x"]=x
                    self.config.write()
                elif self.config["p1x"]!="0" and self.config["p2x"]=="0"  :
                    self.config["p2x"]=x
                    self.config.write()
                    messagebox.showinfo("Calibrate", "calibration compeleted!")




        def updateShow(self):
            # Get a frame from the video source
            cap=cv2.VideoCapture(0)
            screen = screeninfo.get_monitors()[0]
            width, height = screen.width, screen.height
            while True:    
                if(cap.isOpened()):
                    #read the frame from cap
                    ret, frame = cap.read()
        
                    if ret:

                        #show frame in main window

                        cv2.namedWindow('ffrm', cv2.WND_PROP_FULLSCREEN)
                        cv2.moveWindow('ffrm', screen.x - 1, screen.y - 1)
                        cv2.setWindowProperty('ffrm', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                        cv2.setMouseCallback("ffrm", self.DoCalibrate)
                        cv2.imshow('ffrm',frame)
                        cv2.waitKey(5)
                        self.root.focus_force()
                    else:
                        break
                        raise ValueError("Unable to open video source", video_source)
       
       
                    if self.show_switch==False:
                        cv2.destroyWindow('ffrm')
                        cap.release()
                        return False
                time.sleep(0.0416666666666667)
        
            #release the cap
            cap.release()

        def showStram(self):
        
            if self.show_switch:
                self.showButton["text"]="StartStream"
                # self.showButton.configure(image=self.playIcon)
                self.show_switch=False
            
            else:
                self.showButton["text"]="StopStream"
                self.show_switch=True
                # self.showButton.configure(image=self.stopIcon)
                self.showTimer=threading.Thread(target=self.updateShow,args=())
                #self.showTimer.daemon=True
                self.showTimer.start()

App(tk.Tk(), "Main")