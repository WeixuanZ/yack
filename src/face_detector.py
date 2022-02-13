from pathlib import Path

import numpy as np
import cv2

from structures import Rect


class FaceDetector:
    def find_speaker_face(self, frame: np.ndarray) -> Rect:
        raise NotImplementedError()


class FaceDetectorDNN(FaceDetector):
    def __init__(
        self,
        model_path=Path("opencv_model", "opencv_face_detector_uint8.pb"),
        config_path=Path("opencv_model", "opencv_face_detector.pbtxt"),
        detection_threshold=0.5,
    ):
        self.model = cv2.dnn.readNetFromTensorflow(str(model_path), str(config_path))
        self.detection_threshold = detection_threshold

    def find_speaker_face(self, frame):
        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (300, 300), [104, 117, 123], False, False
        )

        self.model.setInput(blob)
        possible_face_detections = self.model.forward()

        # find the minimum bounding box that contains all speakers
        min_x, min_y = frame.shape[1], frame.shape[0]
        max_x, max_y = 0, 0

        for i in range(possible_face_detections.shape[2]):
            face = possible_face_detections[0, 0, i]
            if face[2] > self.detection_threshold:
                x1 = int(face[3] * frame.shape[1])
                y1 = int(face[4] * frame.shape[0])
                x2 = int(face[5] * frame.shape[1])
                y2 = int(face[6] * frame.shape[0])

                min_x, min_y = min(min_x, x1), min(min_y, y1)
                max_x, max_y = max(max_x, x2), max(max_y, y2)

        if min_x > max_x or min_y > max_y:
            # Can't find a face, default to the whole image
            min_x, min_y = 0, 0
            max_x, max_y = frame.shape[1], frame.shape[0]

        speakers_bb = Rect(
            min_x,
            min_y,
            (max_x - min_x),
            (max_y - min_y),
        )

        return speakers_bb


class FaceDetectorCascade(FaceDetector):
    def __init__(
        self, model_path=Path("opencv_model", "haarcascade_frontalface_default.xml")
    ):
        self.model = cv2.CascadeClassifier(str(model_path))

    def find_speaker_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        face_rects = self.model.detectMultiScale(gray, 1.1, 6)

        # find the minimum bounding box that contains all speakers
        min_x, min_y = frame.shape[1], frame.shape[0]
        max_x, max_y = 0, 0

        for (x, y, w, h) in face_rects:
            # extend text exclusion bounding box to include speaker
            min_x, min_y = min(x, min_x), min(y, min_y)
            max_x, max_y = max(x, x + w), max(y, y + h)

        if min_x > max_x or min_y > max_y:
            # Can't find a face, default to the whole image
            min_x, min_y = 0, 0
            max_x, max_y = frame.shape[1], frame.shape[0]

        speakers_bb = Rect(
            min_x,
            min_y,
            (max_x - min_x),
            (max_y - min_y),
        )

        return speakers_bb


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    face_detector = FaceDetectorDNN()

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()

        speakers_bb = face_detector.find_speaker_face(frame)

        cv2.rectangle(
            frame,
            (speakers_bb.x, speakers_bb.y),
            (
                speakers_bb.x + speakers_bb.width,
                speakers_bb.y + speakers_bb.height,
            ),
            (255, 0, 0),
            2,
        )

        cv2.imshow("Face", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
