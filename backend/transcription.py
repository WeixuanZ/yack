from typing import Coroutine, OrderedDict

from deepgram import Deepgram
from dotenv import dotenv_values

from av import load_audio

secrets: OrderedDict = dotenv_values(".secrets")


def transcribe(filename: str) -> Coroutine:
    dg_client = Deepgram(secrets["DEEPGRAM_API_KEY"])

    source = {"buffer": load_audio(filename), "mimetype": "audio/wav"}

    return dg_client.transcription.prerecorded(
        source, {"punctuate": True, "diarize": True, "utterances": True}
    )
