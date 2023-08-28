import cv2
import numpy as np
import screeninfo
from configobj import ConfigObj
# Initialize the camera capture
cap = cv2.VideoCapture(0)  # 0 represents the default camera
def edit_mask():
    #read monitor information
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    config = ConfigObj('conf.cnf')

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()

        #read frame from video and convert to gray then thresh then find edge
        if config["Ds"]=="top":
            frame = cv2.flip(frame, 1)
        elif  config["Ds"]=="down":
            frame = cv2.flip(frame, 0)

        masked = np.zeros_like(frame)
        # Variables to keep track of drawing state
        drawing = False
        points = []

        def draw_shape(event, x, y, flags, param):
            global drawing, points
            # Clear the canvas for a new shape

            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                points = [(x, y)]

            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing:
                    points.append((x, y))
                    mask_temp = frame.copy()
                    for i in range(1, len(points)):
                        cv2.line(mask_temp, points[i-1], points[i], (0, 0, 255), 2)
                    cv2.imshow('masked', mask_temp)

            elif event == cv2.EVENT_LBUTTONUP:
                if drawing:
                    drawing = False
                    points.append((x, y))
                    cv2.fillPoly(frame, [np.array(points)], (255, 255, 255))
                    cv2.fillPoly(masked, [np.array(points)], (255, 255, 255))
                    points = []

        cv2.namedWindow('masked')
        cv2.setMouseCallback('masked', draw_shape)

        while True:
            cv2.namedWindow('masked', cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow('masked', screen.x - 1, screen.y - 1)
            cv2.setWindowProperty('masked', cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow('masked', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                cv2.imwrite('masked.png', masked)
                cv2.destroyAllWindows()
                cap.release()  # Release the camera
                break  # Exit the loop

        # Close all windows
        cv2.destroyAllWindows()
        cap.release()  # Release the camera
        break  # Exit the outer loop
