import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
from configobj import ConfigObj
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
class sett:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # create the main sections of the layout, 
        # and lay them out
        self.left = Frame(window)
        self.right = Frame(window)
        self.left.pack(side=LEFT)
        self.right.pack(side=RIGHT)
       
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
        
        #chekbox widget for niddle is top or down 
        self.lbl3=tk.Label(window,text="Niddle Position")
        self.lbl3.pack(in_=self.right)
        self.dsCombo=ttk.Combobox(window, state="readonly",value=['top', 'down'])  
        self.dsCombo.pack(in_=self.right)
        
        #textbox widget for Analysis Speed in second
        self.lbl4=tk.Label(window,text="Analysis Speed(ms)")
        self.lbl4.pack(in_=self.right)
        self.SpeedVar=StringVar()
        self.SpeedText=tk.Entry(window,textvariable=self.SpeedVar)
        self.SpeedText.pack(in_=self.right)

        #submit button for changes 
        self.btnSave=tk.Button(window,text="save changes!",command=self._do_config)
        self.btnSave.pack(in_=self.right)
        
 

        self.config=ConfigObj('conf.cnf')
        #set config values from file to widgets
        self.thSlider.set(self.config["cannyth1"])
        self.brightslider.set(self.config["bright"])
        self.dsCombo.set(self.config["Ds"])
        self.SpeedVar.set(self.config["interval"])

        self.window.mainloop()
    def _do_config(self):
        print('')

    def fire(self):
        sett(tk.Tk(), "DropVision Setting")


