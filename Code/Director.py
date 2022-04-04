import mediapipe as mp

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

    def GetCommand(self, handLMs):
        fingiePoint1 = handLMs.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        fingiePoint2 = handLMs.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_DIP]

        x = round((fingiePoint2.x - fingiePoint1.x) * 1000)
        y = round((fingiePoint2.y - fingiePoint1.y) * 1000)
        z = round((fingiePoint2.z - fingiePoint1.z) * 1000)

        #if x > 0 and x < 20:
        #    x = 20
        #elif x < 0 and x > - 20:
        #    x = -20

        #if y > 0 and y < 20:
        #    y = 20
        #elif y < 0 and y > - 20:
        #    y = -20

        #if z > 0 and z < 20:
        #    z = 20
        #elif z < 0 and z > - 20:
        #    z = -20

        telloCommand = "go " + str(x) + " " + str(y) + " " + str(z) + " " + str(max(abs(x), abs(y), abs(z)))
        return telloCommand