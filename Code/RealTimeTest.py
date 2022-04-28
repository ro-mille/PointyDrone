import mediapipe as mp
import cv2
import numpy as np

from tello_dummy import Tello
from Gestures import Gestures, GestureDetector
from Director import DirectionDetector
from Timer import Timer

hands = mp.solutions.hands.Hands()
gest_detect = GestureDetector()
direction_detect = DirectionDetector()

tello = Tello()


cap = cv2.VideoCapture(0)

write_video = False

writer = None
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


# Predicted class for open/close
pred_class = Gestures.NONE

# Which hand controls start/stop
ControlHand = None

# Buffers for containing delta times for when either hand is OPEN
timer = Timer()
GestSeries = {'Right': [], 'Left': [], 'Total': []}
time_buffer_size = timer.one_second * 2

while cap.isOpened() and ControlHand is None:
    success, original_image = cap.read()
    if not success:
        continue

    h, w, c = original_image.shape
    new_w = 320
    aspect = h/w
    original_image = cv2.resize(original_image, (round(new_w), round(new_w*aspect)))
    if write_video and writer is None:
        writer = cv2.VideoWriter('Processed.mp4', fourcc, 30, (round(new_w), round(new_w*aspect)))

    image = np.copy(original_image)
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h,w,c = image.shape
    result = hands.process(image)
    hand_landmarks = result.multi_hand_landmarks
    last_gests = []
    if hand_landmarks:
        ## TODO Change to do this one time per image (as opposed to one time per hand)
        for handIdx, handLMs in enumerate(hand_landmarks):
            hand_class = result.multi_handedness[handIdx].classification[0]
            bbox_color = (255, 0, 0) if hand_class.label == 'Right' else (0, 255, 0)
            last_gests += [(gest_detect.getHandGesture(original_image, handLMs, bbox_color=bbox_color), hand_class.label)]

        CurGest = {'Right': Gestures.NO_CONF, 'Left': Gestures.NO_CONF}
        for gest in last_gests:
            CurGest[gest[1]] = Gestures(gest[0])
            color = (255, 0, 0) if gest[1] == 'Right' else (0, 255, 0)
            pos = (0, h-10) if gest[1] == 'Right' else (0, 60)
            cv2.putText(original_image, str(Gestures(gest[0])), pos, cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)

        time_between_frames = timer.GetDelta()
        GestSeries['Right'] += [time_between_frames if CurGest['Right'] == Gestures.CLOSED else 0.0]
        GestSeries['Left'] +=  [time_between_frames if CurGest['Left'] == Gestures.CLOSED else 0.0]
        GestSeries['Total'] += [time_between_frames]

    ## Maintain a buffer of the last X second of gesture time deltas
    crop_indx = 0
    while sum(GestSeries['Total'][crop_indx:]) > time_buffer_size:
        crop_indx += 1
    GestSeries['Right'] = GestSeries['Right'][crop_indx:]
    GestSeries['Left']  = GestSeries['Left'][crop_indx:]
    GestSeries['Total'] = GestSeries['Total'][crop_indx:]

    ## Sum over time-frames
    RightClosed = sum(GestSeries['Right'])
    LeftClosed = sum(GestSeries['Left'])
    TotalTime = max(sum(GestSeries['Total']), time_buffer_size)
    if  RightClosed > (TotalTime / 2) and LeftClosed < (TotalTime / 4):
        ControlHand = 'Right'
    elif LeftClosed > (TotalTime / 2) and RightClosed < (TotalTime / 4):
        ControlHand = 'Left'

    cv2.imshow("Hand",original_image)
    if write_video and writer is not None:
        writer.write(original_image)
    cv2.waitKey(1)

print('ControlHand is {}'.format(ControlHand))

frame_count = 0

last_command = 'takeoff'
LastGesture = Gestures.NONE
timer.Restart()
time_between_direction_updates = timer.one_second*0.1
last_command_time = time_between_direction_updates
#tello.send_command("takeoff")
while cap.isOpened():
    success, original_image = cap.read()
    if not success:
        break
    h, w, c = original_image.shape
    new_w = 320
    aspect = h / w
    original_image = cv2.resize(original_image, (round(new_w), round(new_w * aspect)))

    image = np.copy(original_image)
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    h,w,c = image.shape
    result = hands.process(image)
    hand_landmarks = result.multi_hand_landmarks
    telloCommand = None
    if hand_landmarks:
        hand_class = result.multi_handedness[0].classification[0]
        if hand_class.label == ControlHand:
            control_idx = 0
            direction_idx = 1
        else:
            control_idx = 1
            direction_idx = 0

        if control_idx < len(hand_landmarks):
            color = (255, 0, 0) if ControlHand == 'Right' else (0, 255, 0)
            pred_class = gest_detect.getHandGesture(original_image, hand_landmarks[control_idx], bbox_color=color)
            pos = (0,h-10)
            cv2.putText(original_image,str(Gestures(pred_class)), pos, cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)
            LastGesture = Gestures(pred_class)

        if direction_idx < len(hand_landmarks):
            handLMs = hand_landmarks[direction_idx]
            direction_detect.drawOverHands(original_image, handLMs)
            telloCommand = direction_detect.GetCommand(handLMs,w,h,image)

    last_command_time += timer.GetDelta()
    if LastGesture == Gestures.CLOSED:
        if telloCommand is not None:
            telloCommand = telloCommand.split(' ')[1:]
        else:
            telloCommand = ['']
        last_command = 'stop ' + ' '.join(telloCommand)
        #tello.send_command(last_command)
    elif LastGesture == Gestures.OPEN and last_command_time > time_between_direction_updates and telloCommand is not None:
        last_command = telloCommand
        #tello.send_command(telloCommand)
        last_command_time = 0
    elif LastGesture == Gestures.OPEN:
        tello.send_command('continue')

    cv2.putText(original_image, last_command, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 4)
    frame_count += 1
    cv2.imshow("Hand",original_image)
    if write_video and writer is not None:
        writer.write(original_image)
    # Check for escape key press to quit
    if (cv2.waitKey(1) & 0xFF) == 27:
        break

tello.send_command('stop')
cap.release()
if write_video and writer is not None:
    writer.release()

tello.plot()


