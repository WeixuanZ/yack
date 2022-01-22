import json
from pathlib import Path
from random import randint
from typing import Callable, List

from flask import Flask, abort, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from face_detector import FaceDetector
from structures import ImageData, Segment
from transcription import split_utterances, transcribe
from video_processor import Video
from frame_processor import StyleTransfer


DEBUG = True


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
    transfer_style = StyleTransfer()
    keyframe = segment.frames[segment.keyframe_index]
    keyframe = transfer_style(keyframe)
    speaker_loc, speaks_bbox = face_detector.find_speaker_face(keyframe)

    segment.speaker_location = speaker_loc
    segment.keyframe = ImageData(image_data_matrix=keyframe, image_subject=speaks_bbox)


async def main():
    video = Video("metaverse_short.mp4")
    utterances = split_utterances(await transcribe(video.audio))

    if DEBUG:
        with open("transcript.json", "w") as file:
            json.dump(utterances, file, indent=4)

    pipeline = pipe(attach_frames(video), get_key_frame_index, process_keyframe)
    segments = pipeline(
        [Segment(**utterance_segment) for utterance_segment in utterances]
    )

    return segments


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/", methods=["GET"])
def serve_home():
    return render_template("index.html")


@app.after_request
def chrome_connection_hack(resp):
    resp.headers["Connection"] = "close"
    return resp


@app.route("/api/submit", methods=["POST"])
def process_video():
    print(request.files)

    if "file" not in request.files:
        return abort(400)

    data = request.files["file"]

    path = Path(".") / app.config["UPLOAD_FOLDER"] / secure_filename(data.filename)
    with open(path.resolve(), "wb") as file:
        data.save(file)

    return redirect(url_for("static", filename="test.jpg"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, threaded=True)
