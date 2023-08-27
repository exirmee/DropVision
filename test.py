import cv2
import numpy as np

# Initialize the camera capture
cap = cv2.VideoCapture(0)  # 0 represents the default camera

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()
    
    # Convert frame to grayscale for contour detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    invert = 255 - thresh
   #ماسک کردن دایره در تصویر جهت محاسبه دقیقتر
    masked_img = cv2.imread('canvas.png')
    masked_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY) 
    masked_data = cv2.bitwise_and(invert, invert, mask=masked_img)

    contours, _ = cv2.findContours(masked_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    
    contour_image = frame.copy()
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
    
    # Display the processed frame
    cv2.imshow('Camera Feed with Contours', contour_image)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
