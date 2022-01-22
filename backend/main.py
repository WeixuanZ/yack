import asyncio
import json

from transcription import transcribe
from video_processor import Video


async def main():
    video = Video("metaverse_short.mp4")
    transcript = await transcribe(video.audio)
    print(json.dumps(transcript, indent=4))
    print(type(transcript))


if __name__ == "__main__":
    asyncio.run(main())
