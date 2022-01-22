from typing import Coroutine, OrderedDict

from deepgram import Deepgram
from dotenv import dotenv_values

secrets: OrderedDict = dotenv_values(".secrets")


def transcribe(audio: bytes) -> Coroutine:
    dg_client = Deepgram(secrets["DEEPGRAM_API_KEY"])

    source = {"buffer": audio, "mimetype": "audio/wav"}

    return dg_client.transcription.prerecorded(
        source, {"punctuate": True, "diarize": True, "utterances": True}
    )
