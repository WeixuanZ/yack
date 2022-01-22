import asyncio
import json
from typing import Callable

from transcription import transcribe
from video_processor import Video, attach_frames


def pipe(*functions: Callable[..., dict]) -> Callable[..., dict]:
    "Implements function composition."

    def pipeline(**state) -> dict:
        for function in functions:
            if ret := function(**state):
                state.update(ret)

        return state

    return pipeline


async def main():
    video = Video("metaverse_short.mp4")
    utterances = await transcribe(video.audio)

    with open("transcript.json", "w") as file:
        json.dump(utterances, file, indent=4)

    pipeline = pipe(attach_frames)
    pipeline(utterances=utterances, video=video)

    pass


if __name__ == "__main__":
    asyncio.run(main())
