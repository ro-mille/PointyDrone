from math import floor
import mediapipe as mp
import pyrealsense2.pyrealsense2 as rs

class DirectionDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def drawOverHands(self, original_image, handLMs):
        self.mp_drawing.draw_landmarks(
            original_image,
            handLMs,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style())

    def GetCommand(self, handLMs, imageW, imageH, depth_image):
        fingiePoint1 = handLMs.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        fingiePoint2 = handLMs.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP] #changed from dip to PIP which is above base of finger -jd

        #remap pixel coordinates for depth values within range of image
        pixelX1 = min(max(floor(fingiePoint1.x * imageW * 2),0),639)
        pixelY1 = min(max(floor(fingiePoint1.y * imageH * 2),0),639)
        pixelX2 = min(max(floor(fingiePoint2.x * imageW * 2),0),639)
        pixelY2 = min(max(floor(fingiePoint2.y * imageH * 2),0),639)

        #scaling x y z directions for drone
        x = max(min(round((fingiePoint2.x - fingiePoint1.x) * 500),100),-100)
        y = max(min(round((fingiePoint2.y - fingiePoint1.y) * 500),100),-100)
        z = max(min(round((depth_image.get_distance(pixelX1,pixelY1) - depth_image.get_distance(pixelX2,pixelY2)) * 1000),75),-75)

        #print(f'X1 {pixelX1} Y1 {pixelY1} X2 {pixelX2} Y2 {pixelY2}')
        #print(f'Distance from camera: {depth_image.get_distance(pixelX1,pixelY1) - depth_image.get_distance(pixelX2,pixelY2)}')
        #print(f'Distance from mediapipe: {z}')

        #drone can only take directions greater than magnitude 20
        if x > 0 and x < 20:
            x = 20
        elif x < 0 and x > - 20:
            x = -20

        if y > 0 and y < 20:
            y = 20
        elif y < 0 and y > - 20:
            y = -20

        if z > 0 and z < 20:
            z = 20
        elif z < 0 and z > - 20:
            z = -20

        #string for drone command
        telloCommand = "go " + str(z) + " " + str(x) + " " + str(y) +  " " + str(max(abs(x), abs(y), abs(z)))
        return telloCommand