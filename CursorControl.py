import cv2

# Try to open and access the available camera on device
mainCamera = cv2.VideoCapture(0) # this zero trys to access the only camera on device, if more exists you can increment if needed

if not mainCamera.isOpened():
    print("Cannot open camera")
    exit()


while True:
    ret, frame = mainCamera.read()
    if not ret:
        print("Can't receive frame. Exiting ...")
        break

    frame = cv2.flip(frame, 1)
    cv2.imshow("Live Video", frame)
    if (cv2.waitKey(1)==ord('q')):
        break
mainCamera.release()
cv2.destroyAllWindows()