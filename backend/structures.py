import cv2
import random


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
        self.uri = f"../data/temp{random.randint(0, 1<<30)}.png"
        cv2.imwrite(self.uri, image_data_matrix)
        self.data = image_data_matrix
        self.subject = image_subject
        self.rect = Rect(0, 0, image_data_matrix.shape[1], image_data_matrix.shape[0])
        self.priority = image_importance


class SpeechData:
    def __init__(self, speech_text) -> None:
        self.speech_text = speech_text


class FrameData:
    def __init__(
        self,
        timestamp: float,
        image: ImageData,
        speech: SpeechData,
        speaker_location: Rect = None,
    ) -> None:
        self.timestamp = timestamp
        self.image = image
        self.speech = speech
        self.speaker_location = speaker_location
