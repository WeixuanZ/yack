import imutils
from imutils import face_utils
import numpy as np
import dlib
import cv2
from structures import Rect


class FaceDetector:
    def __init__(self):
        self.DETECTOR = dlib.get_frontal_face_detector()
        self.PREDICTOR = dlib.shape_predictor(r".\dlib_shape_predictor\shape_predictor_68_face_landmarks.dat")

    def find_speaker_face(self, frame):
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.DETECTOR(gray, 1)

        # this is the default speaker face position
        speaker_face = Rect((frame.shape[0] // 2) - 10, (frame.shape[1] // 2) - 10,
                            (frame.shape[0] // 2) + 10, (frame.shape[1] // 2) + 10)
        speaker_mouth_ratio = 0.0

        if len(rects) == 0:
            return speaker_face
        
        for (i, rect) in enumerate(rects):
            shape = self.PREDICTOR(gray, rect)
            shape = face_utils.shape_to_np(shape)
            
            mouth_open = max(dist(shape[61], shape[67]), dist(shape[62], shape[66]), dist(shape[63], shape[65]))
            mouth_width = dist(shape[54], shape[48])
            
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            if (mouth_open / mouth_width) > speaker_mouth_ratio:
                speaker_mouth_ratio = (mouth_open / mouth_width)
                speaker_face = Rect(x, y, w, h)
        
        return speaker_face


def dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
