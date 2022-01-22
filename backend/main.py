import asyncio
import json
from typing import Callable, List
from random import randint

from structures import ImageData, Segment
from transcription import transcribe, split_utterances
from video_processor import Video
from face_detector import FaceDetector


def pipe(
    *functions: Callable[[Segment], None]
) -> Callable[[List[Segment]], List[Segment]]:
    """Implements function composition."""

    def pipeline(segments):
        for segment in segments:
            for function in functions:
                function(segment)

        return segments

    return pipeline


def attach_frames(video: Video):
    def attach_to_segment(segment: Segment) -> None:
        segment.frames = video.get_frames(segment.start, segment.end)

    return attach_to_segment


def get_key_frame_index(segment: Segment) -> None:
    segment.keyframe_index = randint(0, segment.frames.shape[0] - 1)


def process_keyframe(segment: Segment) -> None:
    face_detector = FaceDetector()
    keyframe = segment.frames[segment.keyframe_index]
    speaker_loc, speaks_bbox = face_detector.find_speaker_face(keyframe)

    segment.speaker_location = speaker_loc
    segment.keyframe = ImageData(image_data_matrix=keyframe, image_subject=speaks_bbox)


async def main():
    video = Video("metaverse_short.mp4")
    utterances = split_utterances(await transcribe(video.audio))

    with open("transcript.json", "w") as file:
        json.dump(utterances, file, indent=4)

    pipeline = pipe(attach_frames(video), get_key_frame_index, process_keyframe)
    segments = pipeline(
        [Segment(**utterance_segment) for utterance_segment in utterances]
    )

    return segments


if __name__ == "__main__":
    asyncio.run(main())
