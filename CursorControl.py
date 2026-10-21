import cv2
import mediapipe as mp

mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils

#Confidence scores are thresholds for what is detected as a hand on the feed. Anything lower than the selected variable is thrown out.
# Same process for tracking if a hand moves too fast or is too blurry it will drop  the confidence value. Thus, not registering hand detection.
hands = mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Try to open and access the available camera on device
# The zero trys to aGo ccess the only camera on device, if more exists you can increment if needed
mainCamera = cv2.VideoCapture(0)

if not mainCamera.isOpened():
    print(f"Cannot open selected camera.")
    exit()

#Once the camera is able to be opened
while True:
    # Capture the boolean value (frameExistsBool) whether it is captured
    # Captures the frame (image) from the read
    frameExistsBool, frame = mainCamera.read()

    # If a frame cannot be captured, it pushes an error to terminal
    if not frameExistsBool:
        print("Can't receive frame. Exiting ...")
        break

# Mirrors frame so it looks correct on screen and refresh every millisecond
    frame = cv2.flip(frame, 1)

# First assumption this captures the matricies in each frame the video stream (RBG matiricies)
    rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    #This seems to show a drawing on the landmarks on the hand over the video stream
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS)

# Creates window with title and image data
    cv2.imshow("Live Video", frame)

# Checks every second to see if q is pressed to quit application
    if (cv2.waitKey(1)==ord('q')):
        break

# No longer holds onto capture stream and kills any open windows
mainCamera.release()
cv2.destroyAllWindows()