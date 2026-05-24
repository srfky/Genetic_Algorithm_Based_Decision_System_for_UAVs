import cv2
import os

counter = 1
max_frames = 5

current_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(current_dir, 'video.mp4')
cap = cv2.VideoCapture(video_path)

save_dir = os.path.join(current_dir, "images")

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

if not cap.isOpened():
    print(f"Error: Video file could not be found! Searched path: {video_path}")
else:
    # Get the frames per second (FPS) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Set how many seconds you want to skip between each captured frame
    seconds_between_frames = 3
    frame_jump = seconds_between_frames * fps

    print("Video opened successfully, capturing frames...")
    while counter <= max_frames:
        ret, frame = cap.read()
        
        if not ret:
            print(f"Error: Frame {counter} could not be read. The video might have ended or be corrupted.")
            break
            
        frame = cv2.resize(frame, (640, 480))
        
        file_path = os.path.join(save_dir, f"photograph-{counter}.jpg")
        
        is_saved = cv2.imwrite(file_path, frame)
        
        if is_saved:
            print(f"SUCCESS: Saved to {file_path}")
        else:
            print(f"FAILED: Frame read successfully but COULD NOT BE WRITTEN to {file_path}")
        
        # Get the current frame position and skip forward
        current_frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_pos + frame_jump)
        
        counter += 1

cap.release()
cv2.destroyAllWindows()