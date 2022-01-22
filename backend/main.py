import asyncio
import json
from typing import Callable, List
from random import randint

from transcription import transcribe, split_utterances
from video_processor import Video


def pipe(*functions: Callable[[dict], None]) -> Callable[[List[dict]], dict]:
    "Implements function composition."

    def pipeline(segments) -> dict:
        for segment in segments:
            for function in functions:
                function(segment)

        return segments

    return pipeline


def attach_frames(video: Video):
    def attach_to_segment(segment: dict) -> None:
        segment["frames"] = video.get_frames(segment["start"], segment["end"])

    return attach_to_segment


def get_key_frame_index(segment: dict) -> None:
    segment["keyframe_index"] = randint(0, segment["frames"].shape[0])


async def main():
    video = Video("metaverse_short.mp4")
    utterances = split_utterances(await transcribe(video.audio))

    with open("transcript.json", "w") as file:
        json.dump(utterances, file, indent=4)

    pipeline = pipe(attach_frames(video), get_key_frame_index)
    segments = pipeline(utterances)

    return segments


if __name__ == "__main__":
    asyncio.run(main())
