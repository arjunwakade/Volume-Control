import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.HandDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
length = 18
vol = 0
volPerc = 0

while True:
    data, frame = cap.read()
    frame = cv2.flip(frame, 1)
    lmList, frame = detector.findHands(frame)
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    if len(lmList) != 0:
        print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(frame, (x1,y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2,y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (cx,cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1,y1), (x2,y2), (255, 0, 255), 3)
        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        # Hand range 15 - 170
        # Volume range -65 - 0

        vol = np.interp(length, [15,170], [minVol, maxVol])
        print(vol)

        volume.SetMasterVolumeLevel(vol, None)

        if length < 18:
            cv2.circle(frame, (cx,cy), 10, (0, 255, 0), cv2.FILLED)
    cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
    height = np.interp(vol, [minVol, maxVol], [400, 150])
    volPerc = np.interp(length, [15, 170], [0, 100])
    cv2.rectangle(frame, (50, int(height)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(frame, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
    cv2.putText(frame, f'{int(volPerc)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

    cv2.imshow("Volume", frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()