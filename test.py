import numpy as np
import cv2

cap = cv2.VideoCapture(1)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur=cv2.GaussianBlur(gray, (7, 7), 0)
        #drop2=118 drop3=180
        flag, thresh = cv2.threshold(blur,118,255 , cv2.THRESH_BINARY)     
        edged=cv2.Canny(thresh,50,100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        #find contours in edged capture, then grab the largest one
        im2, contours, hierarchy = cv2.findContours(edged,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(frame, contours, -1, (0,255,0), 3)
        cv2.imshow('edged',frame)
        # write the flipped frame
        #out.write(edged)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
