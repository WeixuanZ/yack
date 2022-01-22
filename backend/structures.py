class Rect:
    def __init__(self, x, y, width, height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.aspect = width / height


class ImageData:
    def __init__(
        self, image_data_matrix, image_subject: Rect, image_importance=None
    ) -> None:
        self.data = image_data_matrix
        self.subject = image_subject
        self.rect = Rect(0, 0, image_data_matrix.shape[0], image_data_matrix.shape[1])
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
