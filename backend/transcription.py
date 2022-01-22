from typing import OrderedDict
from contextlib import suppress

from deepgram import Deepgram
from dotenv import dotenv_values

secrets: OrderedDict = dotenv_values(".secrets")


def delete_keys(transcript: dict, keys: list):
    for key in keys:
        with suppress(KeyError):
            del transcript[key]

    for value in transcript.values():
        if isinstance(value, dict):
            delete_keys(value, keys)

        if isinstance(value, list):
            for child in value:
                if isinstance(child, dict):
                    delete_keys(child, keys)


def validate_transcript(transcript: dict):
    assert "results" in transcript
    assert "utterances" in transcript["results"]

    utterances: list = transcript["results"]["utterances"]
    assert isinstance(utterances, list)

    for utterance in utterances:
        assert isinstance(utterance, dict)

        assert "start" in utterance
        assert "end" in utterance
        assert "transcript" in utterance
        assert "speaker" in utterance


async def transcribe(audio: bytes) -> list:
    dg_client = Deepgram(secrets["DEEPGRAM_API_KEY"])

    source = {"buffer": audio, "mimetype": "audio/wav"}

    transcript = await dg_client.transcription.prerecorded(
        source, {"punctuate": True, "diarize": True, "utterances": True}
    )

    delete_keys(
        transcript, ["metadata", "channel", "channels", "words", "id", "confidence"]
    )

    validate_transcript(transcript)

    return transcript["results"]["utterances"]
