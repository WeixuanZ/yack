import asyncio
import json

from transcription import transcribe
from video_processor import Video, attach_frames


async def main():
    video = Video("metaverse_short.mp4")
    utterances = await transcribe(video.audio)

    with open("transcript.json", "w") as file:
        json.dump(utterances, file, indent=4)

    attach_frames(utterances, video)


if __name__ == "__main__":
    asyncio.run(main())
