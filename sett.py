import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
from configobj import ConfigObj
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import threading


class sett():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

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
        self.SpeedText=tk.Scale(window,from_=1,to=2000,orient="horizontal")
        self.SpeedText.pack(in_=self.right)
  
        #chekbox widget for niddle is top or down 
        self.lbl3=tk.Label(window,text="Niddle Position")
        self.lbl3.pack(in_=self.right)
        self.dsCombo=ttk.Combobox(window, state="readonly",value=['top', 'down'])  
        self.dsCombo.pack(in_=self.right)
        
        #preview button 
        self.btnPre=tk.Button(window,text="Preview!",command=self.start_preview)
        self.btnPre.pack(in_=self.right)

        #submit button for changes 
        self.btnSave=tk.Button(window,text="save changes!",command=self._do_config)
        self.btnSave.pack(in_=self.right)
        
 

        self.config=ConfigObj('conf.cnf')
        #set config values from file to widgets
        self.CamCombo.set(self.config["path"])
        self.thSlider.set(self.config["cannyth1"])
        self.brightslider.set(self.config["bright"])
        self.dsCombo.set(self.config["Ds"])
        self.SpeedText.set(self.config["interval"])

        
        self.window.mainloop()
    def start_preview(self):
        t=threading.Thread(target=self.show_preview)
        t.start()
    def show_preview(self):
        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        cap = cv2.VideoCapture(self.config["path"])
        # Check if camera opened successfully
        if (cap.isOpened()== False): 
          print("Error opening video stream or file")
 
        # Read until video is completed
        while(cap.isOpened()):
          # Capture frame-by-frame
          ret, frame = cap.read()
          if ret == True:
            #read configuration file and put it to config array
            config = ConfigObj('conf.cnf')
            #do prosecc on  raw image frame  
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur=cv2.GaussianBlur(gray, (7, 7), 0)
            #drop2=118 drop3=180
            flag, thresh = cv2.threshold(blur,int(config["cannyth1"]),255 , cv2.THRESH_BINARY)     
            edged=cv2.Canny(thresh,50,100)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            
            weighted = cv2.addWeighted(frame, 1, frame, 0.1, 0)
            ret, mask = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY_INV)
            sum = cv2.add(frame, frame, mask=edged)

            
            #Display the resulting frame
            cv2.imshow('preview',sum)
            
            #clear the config object
            ConfigObj.clear(config)
            
            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
              break
 
          # Break the loop
          else: 
            break
 
        # When everything done, release the video capture object
        cap.release()
 
        # Closes all the frames
        cv2.destroyAllWindows()
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


