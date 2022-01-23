import string
from contextlib import suppress
from textwrap import wrap
from typing import OrderedDict

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


def split_utterances(
    utterances: list, width: int = 50, min_width: int = 20, pause_len: float = 0.5
) -> list:
    out = []

    # TODO: would be nice to get this to merge multiple utterances, but we would
    # have to ensure that the speaker hasn't changed, and that the utterances
    # merged are relatively close in time.
    for utterance in utterances:
        u_len = len(utterance["transcript"])
        u_time = utterance["end"] - utterance["start"]

        # + 1 because the spaces between chunks are removed.
        if u_len <= width + min_width + 1:
            if utterance["transcript"][-1] != ".":
                utterance["transcript"] += "..."
            out.append(utterance)
            continue

        chunks = wrap(utterance["transcript"], width, break_long_words=False)
        assert len(chunks) >= 2

        if len(chunks[-1]) < min_width:
            chunks[-2] += " " + chunks[-1]
            chunks.pop()

        # Add leading ellipsis.
        for i in range(1, len(chunks)):
            chunks[i] = "..." + chunks[i]

        start = utterance["start"]

        # Add empty frames when there's no dialogue.
        if out:
            if start - out[-1]["end"] > pause_len:
                out.append(
                    {
                        "start": out[-1]["end"],
                        "end": start,
                        "transcript": "",
                        "speaker": None,
                    }
                )

        for chunk in chunks:
            end = start + len(chunk) * u_time / u_len

            # Add trailing ellipsis.
            if chunk[-1] in [","]:
                chunk += " "
            if chunk[-1] not in [".", "!"]:
                chunk += "..."

            out.append(
                {
                    "start": start,
                    "end": end,
                    "transcript": chunk,
                    "speaker": utterance["speaker"],
                }
            )

            start = end

    return out


if __name__ == "__main__":
    res = split_utterances(
        [
            {
                "start": 3.1363988,
                "end": 8.490252,
                "transcript": "I believe the Meta is the next chapter for the Internet. And it's the next chapter for our company too.",
                "speaker": 0,
            }
        ]
    )
    print(res)
