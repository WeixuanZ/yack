import ffmpeg
import numpy as np


class Video:
    def __init__(self, path: str, height: int = 500, width: int = 600):
        self.width = width
        self.height = height
        probe = ffmpeg.probe(path)
        self.video_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        self.auto_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "audio"),
            None,
        )

        self.frames = self.load_frames(path, self.height, self.width)
        self.audio = self.load_audio(path)

    @staticmethod
    def load_frames(path: str, height: int, width: int) -> np.ndarray:
        out, _ = (
            ffmpeg.input(path)
            .filter("scale", width, height)
            .output("pipe:", format="rawvideo", pix_fmt="rgb24")
            .run(capture_stdout=True)
        )

        return np.frombuffer(out, np.uint8).reshape([-1, height, width, 3])

    @staticmethod
    def load_audio(path):
        out, _ = (
            ffmpeg.input(path)
            .output("-", format="wav")
            .run(capture_stdout=True, capture_stderr=True)
        )

        return out

    def get_frames(self, start_time: float, end_time: float):
        avg_fps = self.video_info["avg_frame_rate"]
        return self.frames[int(start_time * avg_fps) : int(end_time * avg_fps), :, :, :]


if __name__ == "__main__":
    video = Video("test.mp4")
    print(video.frames.shape)
