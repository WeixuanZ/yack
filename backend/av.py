import ffmpeg
from ffmpeg import Error


def load_audio(filename: str) -> bytes:
    try:
        out, err = (
            ffmpeg.input(filename)
            .output("-", format="wav")
            .run(capture_stdout=True, capture_stderr=True)
        )
    except Error as err:
        print(err.stderr)
        raise

    return out
