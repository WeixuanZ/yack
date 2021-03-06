import base64

import cv2
import numpy as np


class Rect:
    def __init__(self, x, y, width, height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if height == 0:
            self.aspect = 1000  # ≈∞
        else:
            self.aspect = width / height

        self.area = width * height
        self.center = (self.x + self.width // 2, self.y + self.height // 2)

    def __repr__(self) -> str:
        x, y, width, height = self.x, self.y, self.width, self.height
        return f"{x=}, {y=}, {width=}, {height=}"


class ImageData:
    def __init__(
        self, image_data_matrix, image_subject: Rect, image_importance=None
    ) -> None:
        _, buffer = cv2.imencode(".png", image_data_matrix)
        self.b64png = base64.standard_b64encode(buffer)

        self.data = image_data_matrix
        self.subject = image_subject
        self.rect = Rect(0, 0, image_data_matrix.shape[1], image_data_matrix.shape[0])
        self.priority = image_importance


class Segment:
    def __init__(
        self,
        start: float,
        end: float,
        transcript: str,
        speaker: int,
        frames: np.ndarray = None,
        keyframe_index: int = None,
        keyframe: np.ndarray = None,
        speaker_location: Rect = None,
        speakers_bbox: Rect = None,
        image: ImageData = None,
    ):
        self.start = start
        self.end = end
        self.transcript = transcript
        self.speaker = speaker

        self.frames = frames
        self.keyframe_index = keyframe_index
        self.keyframe = keyframe
        self.speaker_location = speaker_location
        self.speakers_bbox = speakers_bbox
        self.image = image
