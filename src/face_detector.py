from pathlib import Path

import cv2
import dlib
from imutils import face_utils

from structures import Rect


class FaceDetector:
    def __init__(self):
        self.DETECTOR = dlib.get_frontal_face_detector()
        # self.PREDICTOR = dlib.shape_predictor(
        #     (
        #         Path(".")
        #         / "src"
        #         / "dlib_shape_predictor"
        #         / "shape_predictor_68_face_landmarks.dat"
        #     ).as_posix()
        # )

    @staticmethod
    def dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def find_speaker_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.DETECTOR(gray, 1)

        # this is the default speaker face position
        speaker_face = Rect(
            ((frame.shape[0] // 2) - 10),
            ((frame.shape[1] // 2) - 10),
            ((frame.shape[0] // 2) + 10),
            ((frame.shape[1] // 2) + 10),
        )

        speaker_mouth_ratio = 0.0

        # find the minimum bounding box that contains all speakers
        min_x = frame.shape[0]
        max_x = 0
        min_y = frame.shape[1]
        max_y = 0

        for rect in rects:
            # shape = self.PREDICTOR(gray, rect)
            # shape = face_utils.shape_to_np(shape)

            # mouth_open = max(
            #     FaceDetector.dist(shape[61], shape[67]),
            #     FaceDetector.dist(shape[62], shape[66]),
            #     FaceDetector.dist(shape[63], shape[65]),
            # )
            # mouth_width = FaceDetector.dist(shape[54], shape[48])

            (x, y, w, h) = face_utils.rect_to_bb(rect)

            # extend text exclusion bounding box to include speaker
            if x < min_x:
                min_x = x
            if x + w > max_x:
                max_x = x + w
            if y < min_y:
                min_y = y
            if y + h > max_y:
                max_y = y + h

            # if (mouth_open / mouth_width) > speaker_mouth_ratio:
            #     speaker_mouth_ratio = mouth_open / mouth_width
            #     speaker_face = Rect(
            #         x,
            #         y,
            #         w,
            #         h,
            #     )

        if min_x > max_x:
            max_x = min_x
            max_y = min_y

        speakers_bb = Rect(
            min_x,
            min_y,
            (max_x - min_x),
            (max_y - min_y),
        )

        return speaker_face, speakers_bb


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    face_detector = FaceDetector()

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow("Input", frame)
        speaker_face, speakers_bb = face_detector.find_speaker_face(frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
