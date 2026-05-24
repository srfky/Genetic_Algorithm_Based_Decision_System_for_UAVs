import cv2 
import numpy as np 
import time 


def calculate_measures_4roi(frame): 
    """
    Define the region of interest (ROI) coordinates
    for lane detection.
    """
    height = frame.shape[0] 
    width = frame.shape[1]  

    corners4roi = [ 
        (0, height), 
        (width / 3.2, height / 1.8),
        (width / 1.5, height / 1.5),
        (width, height)]
    
    return corners4roi 


def region_of_interest(frame, corners4roi): 
    """
    Apply a mask to keep only the selected
    region of interest.
    """
    mask = np.zeros_like(frame) 
    match_mask_color = 255

    cv2.fillPoly(mask, corners4roi, match_mask_color) 
    masked_frame = cv2.bitwise_and(frame, mask) 

    return masked_frame 


def drow_the_lines(frame, lines): 
    """
    Draw detected lane lines on the frame.
    """
    frame = np.copy(frame)  
    blank_frame = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)   

    for line in lines:      
        for x1, y1, x2, y2 in line:
            cv2.line(blank_frame, (x1,y1), (x2,y2), (0, 255, 0), thickness=5)    
          

    frame = cv2.addWeighted(frame, 0.9, blank_frame, 0.5, 0.0) 

    return frame 


def detect_lines_and_process(frame):
    """
    Process each frame and detect lane lines
    using Canny Edge Detection and Hough Transform.
    """
     # Reduce noise with Gaussian Blur
    blurred_frame = cv2.GaussianBlur(frame,(9,9),0.8)  

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_RGB2GRAY) 

    # Detect edges 
    canny_frame = cv2.Canny(gray_frame, 100, 120) 

    # Apply ROI mask 
    cropped_frame = region_of_interest(canny_frame,
                    np.array([calculate_measures_4roi(frame)], np.int32),)
   
    # Detect lines using Probabilistic Hough Transform
    lines = cv2.HoughLinesP(cropped_frame,       
                            rho=2,               
                            theta=np.pi/180,
                            threshold=135,
                            lines=np.array([]),
                            minLineLength=40,
                            maxLineGap=100)
    
    # Draw detected lines
    frame_with_lines = drow_the_lines(frame, lines)
    
    return frame_with_lines


# Read video file
cap = cv2.VideoCapture("Road1.mp4")   


while cap.isOpened(): 

    # Read video frame
    ret, frame = cap.read() 
 
    cv2.imshow("Original Road", frame) 
    
    # Process frame
    frame = detect_lines_and_process(frame) 

    # Slow down playback slightly
    time.sleep(0.01) 

    # Apply ROI for visualization
    cropped_frame = region_of_interest(frame, 
                                   np.array([calculate_measures_4roi(frame)], np.int32),)
    
    cv2.imshow("Cropped Road", cropped_frame)

    cv2.imshow("Processed Road", frame) 

    if cv2.waitKey(1) & 0xFF == ord("q"): 
            break 
    
    
cap.release()
cv2.destroyAllWindows()