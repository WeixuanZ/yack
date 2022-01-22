class ImageData:
    def __init__(self, image_data_matrix, image_importance=None) -> None:
        self.aspect = image_data_matrix.shape[0] / image_data_matrix.shape[1]
        self.data = image_data_matrix
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
        speaker_location=None,
    ) -> None:
        self.timestamp = timestamp
        self.image = image
        self.speech = speech
        self.speaker_location = speaker_location
