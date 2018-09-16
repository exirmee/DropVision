# to create additional windows, you can use Toplevel()
# when you quit the root window the child window also quits

from tkinter import *
    
# create root window
root = Tk()
root.title('root win')
# create child window
top = Toplevel()
top.title('top win')
top.lift(aboveThis=root)
 
root.mainloop()