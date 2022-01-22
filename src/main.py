import asyncio
import pickle
import json
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
from werkzeug.utils import secure_filename

from face_detector import FaceDetector
from frame_processor import StyleTransfer

from layout_generator import LayoutGenerator
from structures import ImageData, Segment
from transcription import split_utterances, transcribe
from video_processor import Video

DEBUG = True

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = (Path(".") / "uploads").resolve()


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


def detect_speaker(segment: Segment) -> None:
    face_detector = FaceDetector()

    segment.keyframe = segment.frames[segment.keyframe_index]
    segment.speaker_location, segment.speakers_bbox = face_detector.find_speaker_face(
        segment.keyframe
    )


def crop_keyframe(segment: Segment) -> None:
    subject_bbox_center = segment.speakers_bbox.center

    # TODO: add margins

    if subject_bbox_center[0] > segment.keyframe.shape[0] // 2:
        segment.keyframe = segment.keyframe[
            :, : int(segment.speakers_bbox.x + segment.speakers_bbox.width), :
        ]
    else:
        segment.keyframe = segment.keyframe[:, int(segment.speakers_bbox.x) :, :]

    if subject_bbox_center[1] > segment.keyframe.shape[1] // 2:
        segment.keyframe = segment.keyframe[
            : int(segment.speakers_bbox.y + segment.speakers_bbox.height), :, :
        ]
    else:
        segment.keyframe = segment.keyframe[int(segment.speakers_bbox.y) :, :, :]


def transfer_keyframe_style(segment: Segment) -> None:
    transfer_style = StyleTransfer()
    segment.keyframe = transfer_style(segment.keyframe)


def convert_keyframe_to_obj(segment: Segment) -> None:
    segment.image = ImageData(
        image_data_matrix=segment.keyframe, image_subject=segment.speakers_bbox
    )


def process_video(path: str) -> str:
    video = Video(path)
    utterances = split_utterances(asyncio.run(transcribe(video.audio)))

    if DEBUG:
        with open("transcript.json", "w") as file:
            json.dump(utterances, file, indent=4)

    pipeline = pipe(
        attach_frames(video),
        get_key_frame_index,
        detect_speaker,
        crop_keyframe,
        transfer_keyframe_style,
        convert_keyframe_to_obj,
    )
    segments = pipeline(
        [Segment(**utterance_segment) for utterance_segment in utterances]
    )

    for segment in segments:
        segment.keyframe = None
        segment.frames = None

    pickle.dump(segments, open("cache.pickle", "wb+"))

    layout = LayoutGenerator()
    for segment in segments:
        layout.add_frame(segment)

    layout.render_frames_to_image("test.svg")
    # FIXME: return the path of the finished comic.
    return "test.svg"


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

    data = request.files["file"]

    # TODO: use tempfile.mkstemp() instead.
    path = (app.config["UPLOAD_FOLDER"] / secure_filename(data.filename)).resolve()

    with open(path, "wb") as file:
        data.save(file)

    comic_filename = process_video(path)

    return redirect(url_for("uploads", name=comic_filename))


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8000, debug=True, threaded=True)
    process_video("metaverse_short.mp4")
