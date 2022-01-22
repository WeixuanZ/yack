import os
import random

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

    def __repr__(self) -> str:
        x, y, width, height = self.x, self.y, self.width, self.height
        return f"{x=}, {y=}, {width=}, {height=}"


class ImageData:
    def __init__(
        self, image_data_matrix, image_subject: Rect, image_importance=None
    ) -> None:
        self.uri = f"./tmp/{random.randint(0, 1<<30)}.png"
        if not os.path.exists("./tmp"):
            os.makedirs("./tmp/")
        cv2.imwrite(self.uri, image_data_matrix)
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
        keyframe: ImageData = None,
        speaker_location: Rect = None,
    ):
        self.start = start
        self.end = end
        self.transcript = transcript
        self.speaker = speaker

        self.frames = frames
        self.keyframe_index = keyframe_index
        self.keyframe = keyframe
        self.speaker_location = speaker_location
