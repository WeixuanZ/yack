import asyncio
import json

from transcription import transcribe
from video_processor import Video


async def main():
    video = Video("metaverse_short.mp4")
    transcript = await transcribe(video.audio)

    with open("transcript.json", "w") as file:
        json.dump(transcript, file, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
