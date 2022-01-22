import asyncio
import json

from transcription import transcribe


async def main():
    transcript = await transcribe("metaverse_short.mp4")
    print(json.dumps(transcript, indent=4))
    print(type(transcript))


if __name__ == "__main__":
    asyncio.run(main())
