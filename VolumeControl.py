import cv2
import mediapipe as mp
import time
import math
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm

# width and height of camera.
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

cTime = 0
pTime = 0

# 0.7: making REALLY sure that it is a hand.
detector = htm.handDetector(min_detection_confidence=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_,
                             CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

'''
pycaw library: 
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# volume.SetMasterVolumeLevel(-20.0, None)
# print(volume.GetVolumeRange()) => (-65.25, 0.0, 0.03125)ie. (min, max, _)
'''

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # lmList[4]: Thumb tip;  lmList[8]: Index-finger tip
        # print(lmList[4], lmList[8]) => [4, 334, 200] [8, 299, 316]

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        length = math.hypot(x2-x1, y2-y1)
        print(length)

        # Our hand range: 40 - 300 aprox
        # Volume range: -65 - 0

        vol = np.interp(length, [40, 300], [minVol, maxVol])
        volBar = np.interp(length, [40, 300], [400, 150])
        volPer = np.interp(length, [40, 300], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 40:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (50, 450),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (50, 70),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
