from operator import truediv
import ffmpeg
import numpy as np


class Video:
    def __init__(
        self,
        path: str,
        fps: int = 1,
        audio_only: bool = False,
    ):
        self.fps = fps

        probe = ffmpeg.probe(path)
        self.video_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        self.audio_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "audio"),
            None,
        )
        if self.audio_info is None:
            raise RuntimeError("Video does not have audio")

        if self.fps > truediv(*map(int, self.video_info["avg_frame_rate"].split("/"))):
            raise RuntimeError("Specified fps higher than raw")
        if float(self.video_info["duration"]) > 120:
            raise RuntimeError("Video longer than 120 seconds")

        if not audio_only:
            self.frames = self.load_frames(
                path, self.video_info["height"], self.video_info["width"], self.fps
            )
        self.audio = self.load_audio(path)

    @staticmethod
    def load_frames(path: str, height: int, width: int, fps: int) -> np.ndarray:
        out, _ = (
            ffmpeg.input(path)
            .filter("fps", fps)
            .filter("scale", width, height)
            .output("pipe:", format="rawvideo", pix_fmt="bgr24")
            .run(capture_stdout=True, capture_stderr=True)
        )

        return np.frombuffer(out, np.uint8).reshape([-1, height, width, 3])

    @staticmethod
    def load_audio(path) -> bytes:
        out, _ = (
            ffmpeg.input(path)
            .output("-", format="wav")
            .run(capture_stdout=True, capture_stderr=True)
        )

        return out

    def get_frames(self, start_time: float, end_time: float) -> np.ndarray:
        frames = self.frames[int(start_time * self.fps) : int(end_time * self.fps)]
        if len(frames) != 0:
            return frames
        return np.array([self.frames[int(start_time * self.fps)]])


if __name__ == "__main__":
    video = Video("metaverse_short.mp4", fps=5)
    print(video.frames.shape)
    print(video.video_info)
