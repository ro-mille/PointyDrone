from tensorflow import keras
import cv2
import numpy as np
from enum import Enum

class Gestures(Enum):
    CLOSED=0
    NONE=1
    OPEN=2
    NO_CONF=3
    def __str__(self):
        return self.name

class GestureDetector():
    def __init__(self):
        self.model = keras.models.load_model("TrainedModel3")
        self.hand_img_size = (127, 127)
        self.model.summary()


    def getHandGesture(self, image, handLMs, bbox_color=(0, 255, 0)):
        h, w, c = image.shape
        x_max = 0
        y_max = 0
        x_min = w
        y_min = h
        for lm in handLMs.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            if x > x_max:
                x_max = x
            if x < x_min:
                x_min = x
            if y > y_max:
                y_max = y
            if y < y_min:
                y_min = y
        # drawing the bounding box
        extra = 25 if w > 400 else 10
        cv2.rectangle(image, (x_min - extra, y_min - extra), (x_max + extra, y_max + extra), bbox_color, 1)
        image = image[max(y_min - extra, 0):min(y_max + extra, h), max(x_min - extra, 0):min(x_max + extra, w)]
        # image = cv2.resize(image, hand_img_size)
        image = np.expand_dims(image, 0)
        pred = self.model.predict(image)
        pred_class = np.argmax(pred)
        if np.max(pred) <= 0.5:
            pred_class = 3
        return pred_class