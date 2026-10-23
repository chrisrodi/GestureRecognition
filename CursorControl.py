import cv2
import mediapipe as mp
import pyautogui
import math
import time

from pyscreeze import screenshot

mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils

# Confidence scores are thresholds for what is detected as a hand on the feed. Anything lower than the selected
# variable is thrown out. Same process for tracking if a hand moves too fast or is too blurry it will drop  the
# confidence value. Thus, not registering hand detection.
hands = mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.7, min_tracking_confidence=0.5)

click_start_time = None
click_times = []
click_cooldown=0.5
scroll_mode=False
freeze_cursor=False
smoothing=0.3     # 0-1, lower is smoother but slower
frame_margin=0.15 # portion of frame edge ignored when mapping to screen
scroll_frames=0     # consecutive frames the scroll gesture has been held (negative = released)
scroll_hold=5       # frames needed to enter/leave scroll mode, stops flickering
scroll_anchor_y=0   # hand height when scroll mode started
scroll_deadzone=0.04
scroll_speed=150    # scroll amount per frame per unit of hand movement from the anchor
screenshot_cooldown=2
last_screenshot_time=0

# Removes moveTo pause between calls so the camera loop is not blocked
pyautogui.PAUSE=0

screen_w,screen_h = pyautogui.size()
print("\n Hand Mouse Gesture Control.")
prev_screen_x=0
prev_screen_y=0

# Try to open and access the available camera on device
# The zero trys to access the only camera on device, if more exists you can increment if needed
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

        # Get Finger Tips
        # Each index represents a specific landmark point on the hand
        thumb_tip=hand_landmarks.landmark[4]
        index_knuckle = hand_landmarks.landmark[5]
        index_tip=hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        fingers = [
            1 if hand_landmarks.landmark[tip].y<hand_landmarks.landmark[tip-2].y else 0
            for tip in [8,12,16,20]
        ]

        # Scroll gesture (all four fingers up) must be held/released for a few frames before switching modes
        if sum(fingers)==4:
            scroll_frames = max(scroll_frames, 0) + 1
        else:
            scroll_frames = min(scroll_frames, 0) - 1

        if not scroll_mode and scroll_frames >= scroll_hold:
            scroll_mode = True
            # Palm center (landmark 9) is steadier than a fingertip
            scroll_anchor_y = hand_landmarks.landmark[9].y
        elif scroll_mode and scroll_frames <= -scroll_hold:
            scroll_mode = False

        #distance between thumb and index
        dist=math.hypot(thumb_tip.x -index_tip.x, thumb_tip.y -index_tip.y)
        if scroll_mode:
            # Scroll speed grows with how far the hand moved from where scroll mode started
            offset = scroll_anchor_y - hand_landmarks.landmark[9].y
            if abs(offset) > scroll_deadzone:
                amount = int((offset - math.copysign(scroll_deadzone, offset)) * scroll_speed)
                if amount:
                    pyautogui.scroll(amount)
                label = "Scroll up" if offset > 0 else "Scroll down"
                cv2.putText(frame,label,(10,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            else:
                cv2.putText(frame,"Scroll mode",(10,90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
        elif dist < 0.06:
            # Only click once per pinch, cursor stays frozen until fingers separate
            if not freeze_cursor:
                freeze_cursor = True
                click_times.append(time.time())

                #Double click check
                if len(click_times)>=2 and click_times[-1]-click_times[-2]<0.4:
                    pyautogui.doubleClick()
                    cv2.putText(frame,"Double Click",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                    click_times=[]
                else:
                    pyautogui.click()
                    cv2.putText(frame,"Single Click",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
        else:
            freeze_cursor = False

        #Move cursor with index finger when not pinching or scrolling
        if not freeze_cursor and not scroll_mode:
            # Map the inner part of the frame to the full screen so edges are reachable
            norm_x = min(max((index_knuckle.x - frame_margin) / (1 - 2 * frame_margin), 0), 1)
            norm_y = min(max((index_knuckle.y - frame_margin) / (1 - 2 * frame_margin), 0), 1)

            # Stay 1px off the edges so pyautogui's corner fail-safe does not trigger
            target_x = 1 + norm_x * (screen_w - 3)
            target_y = 1 + norm_y * (screen_h - 3)

            # Smooth movement to reduce jitter
            screen_x = prev_screen_x + (target_x - prev_screen_x) * smoothing
            screen_y = prev_screen_y + (target_y - prev_screen_y) * smoothing
            pyautogui.moveTo(int(screen_x), int(screen_y))
            prev_screen_x,prev_screen_y=screen_x,screen_y
    else:
        # Hand left the frame, drop out of scroll mode so a stale anchor isn't reused
        scroll_mode=False
        scroll_frames=0

# Creates window with title and image data
    cv2.imshow("Live Video", frame)

# Checks every second to see if q is pressed to quit application
    if (cv2.waitKey(1)==ord('q')):
        break

# No longer holds onto capture stream and kills any open windows
mainCamera.release()
cv2.destroyAllWindows()