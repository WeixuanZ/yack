import os
import pickle
import asyncio
import json
import tempfile
from pathlib import Path
from random import randint
from typing import Callable, List

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from face_detector import FaceDetector
from frame_processor import StyleTransfer

from layout_generator import LayoutGenerator
from structures import ImageData, Segment
from transcription import split_utterances, transcribe
from video_processor import Video

PRODUCTION = os.environ.get("ENV") == "production"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = (Path(".") / "uploads").resolve()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000  # Limit uploads to 16 MB.
app.config["PREFERRED_URL_SCHEME"] = "https"


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


def detect_speaker(face_detector: FaceDetector):
    def face_detector_func(segment: Segment) -> None:
        segment.keyframe = segment.frames[segment.keyframe_index]
        (
            segment.speaker_location,
            segment.speakers_bbox,
        ) = face_detector.find_speaker_face(segment.keyframe)

    return face_detector_func


def crop_keyframe(segment: Segment) -> None:
    subject_bbox_center = segment.speakers_bbox.center

    PADDING = segment.keyframe.shape[0] * 0.2

    if subject_bbox_center[0] > segment.keyframe.shape[1] * 5 / 6:
        segment.keyframe = segment.keyframe[
            :,
            : int(
                min(
                    segment.speakers_bbox.x + segment.speakers_bbox.width + PADDING,
                    segment.keyframe.shape[1],
                )
            ),
            :,
        ]
        segment.speakers_bbox.x -= segment.keyframe.shape[1] - min(
            segment.speakers_bbox.x + segment.speakers_bbox.width + PADDING,
            segment.keyframe.shape[1],
        )
    elif subject_bbox_center[0] < segment.keyframe.shape[1] * 1 / 6:
        segment.keyframe = segment.keyframe[
            :, int(max(segment.speakers_bbox.x - PADDING, 0)) :, :
        ]
        segment.speakers_bbox.x -= int(max(segment.speakers_bbox.x - PADDING, 0))
    else:
        if randint(0, 1):
            segment.keyframe = segment.keyframe[
                :,
                : int(
                    min(
                        segment.speakers_bbox.x + segment.speakers_bbox.width + PADDING,
                        segment.keyframe.shape[1],
                    )
                ),
                :,
            ]
            segment.speakers_bbox.x -= segment.keyframe.shape[1] - min(
                segment.speakers_bbox.x + segment.speakers_bbox.width + PADDING,
                segment.keyframe.shape[1],
            )
        else:
            segment.keyframe = segment.keyframe[
                :, int(max(segment.speakers_bbox.x - PADDING, 0)) :, :
            ]
            segment.speakers_bbox.x -= int(max(segment.speakers_bbox.x - PADDING, 0))

    if randint(0, 1):
        segment.keyframe = segment.keyframe[
            : int(segment.keyframe.shape[1] * 3 / 4), :, :
        ]
        segment.speakers_bbox.y -= segment.keyframe.shape[1] - int(
            segment.keyframe.shape[1] * 3 / 4
        )


def transfer_keyframe_style(segment: Segment) -> None:
    transfer_style = StyleTransfer()
    segment.keyframe = transfer_style(segment.keyframe)


def convert_keyframe_to_obj(segment: Segment) -> None:
    segment.image = ImageData(
        image_data_matrix=segment.keyframe, image_subject=segment.speakers_bbox
    )


def process_video(path: str) -> str:
    video = Video(path, fps=2)
    utterances = split_utterances(asyncio.run(transcribe(video.audio)))

    if not PRODUCTION:
        with open("transcript.json", "w") as file:
            json.dump(utterances, file, indent=4)

    face_detector = FaceDetector()
    pipeline = pipe(
        attach_frames(video),
        get_key_frame_index,
        detect_speaker(face_detector),
        crop_keyframe,
        transfer_keyframe_style,
        convert_keyframe_to_obj,
    )
    segments = pipeline(
        [Segment(**utterance_segment) for utterance_segment in utterances]
    )

    if not PRODUCTION:
        for segment in segments:
            segment.keyframe = None
            segment.frames = None

        pickle.dump(segments, open("cache.pickle", "wb+"))

    layout = LayoutGenerator()
    for segment in segments:
        layout.add_frame(segment)

    _, path = tempfile.mkstemp(
        prefix="out", suffix=".svg", dir=app.config["UPLOAD_FOLDER"]
    )
    layout.render_frames_to_image(path)

    return Path(path).name


@app.route("/", methods=["GET"])
def serve_home():
    return render_template("index.html")


@app.route("/uploads/<name>")
def serve_uploads(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


app.add_url_rule("/uploads/<name>", endpoint="uploads", build_only=True)


@app.after_request
def chrome_connection_hack(resp):
    resp.headers["Connection"] = "close"
    return resp


@app.route("/api/submit", methods=["POST"])
def submit_video_api():
    if "file" not in request.files:
        return abort(400)

    _, path = tempfile.mkstemp(prefix="in", dir=app.config["UPLOAD_FOLDER"])

    try:
        data = request.files["file"]
        data.save(path)

        comic_name = process_video(path)
    finally:
        Path(path).unlink()

    if PRODUCTION:
        return redirect(
            url_for("uploads", name=comic_name, _external=True, _scheme="https")
        )

    return redirect(url_for("uploads", name=comic_name))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, threaded=True)
