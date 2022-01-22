import numpy as np
import drawSvg as draw

from structures import FrameData, ImageData, Rect, SpeechData

COMIC_SPACING_TOLERANCE = 0.2
COMIC_AREA_MIN = 100 * 50
COMIC_PADDING = 5


class UnfilledRegion:
    def __init__(self, region) -> None:
        self.unfilled = Rect(region.x, region.y, region.width, region.height)

    def get_remaining_unfilled_rect(self):
        return self.unfilled

    def get_last_unfilled_position(self):
        return self.unfilled.y + self.unfilled.height

    def claim_chunk(
        self,
        aspect: float,
        min_area: float = COMIC_AREA_MIN,
        tolerance: float = COMIC_SPACING_TOLERANCE,
    ):
        """
        Either return a vertical or horizontal chunk from the unfilled region.
        An attempt is made to match the target aspect ratio.
        """

        v_chunking = Rect(
            self.unfilled.x,
            self.unfilled.y,
            self.unfilled.width,
            min(self.unfilled.height, self.unfilled.width / aspect),
        )
        h_chunking = Rect(
            self.unfilled.x,
            self.unfilled.y,
            min(self.unfilled.width, self.unfilled.height * aspect),
            self.unfilled.height,
        )

        def get_chunked_error(chunking: Rect):
            return abs(chunking.aspect - aspect)

        v_error = get_chunked_error(v_chunking)
        h_error = get_chunked_error(h_chunking)
        if v_error <= h_error and v_error < tolerance and v_chunking.area > min_area:
            self.unfilled.y += v_chunking.height
            self.unfilled.height -= v_chunking.height
            return v_chunking
        elif v_error > h_error and h_error < tolerance and h_chunking.area > min_area:
            self.unfilled.x += h_chunking.width
            self.unfilled.width -= h_chunking.width
            return h_chunking
        else:
            return None


class LayoutGenerator:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame: FrameData):
        self.frames.append(frame)

    def render_frames_to_image(self, file_name: str, width: int):
        frame_rects = self.__get_frame_rects_for_rendering(width, 200)

        height = 1000
        ctx = draw.Drawing(width, height, origin=(0, 0), displayInline=False)
        for rect, frame in zip(frame_rects, self.frames):
            print(rect)
            ctx.append(
                draw.Rectangle(
                    rect.x,
                    height - rect.y - rect.height,
                    rect.width,
                    rect.height,
                    stroke="#F00",
                    fill=None,
                )
            )

        ctx.setPixelScale(1)
        ctx.savePng(file_name)

    def __get_frame_rects_for_rendering(self, page_width: int, max_height: int):
        frame_rects = []
        unfilled = UnfilledRegion(Rect(0, 0, page_width, max_height))
        for frame in self.frames:
            assert isinstance(frame, FrameData)
            frame_rect = unfilled.claim_chunk(frame.image.rect.aspect)
            if frame_rect is None:
                # Failed to claim the chunk: the frame is too large to display in this layout block
                unfilled = UnfilledRegion(
                    Rect(
                        0, unfilled.get_last_unfilled_position(), page_width, max_height
                    )
                )
                frame_rect = unfilled.claim_chunk(frame.image.rect.aspect)
                assert frame_rect is not None

            frame_rects.append(frame_rect)

        return frame_rects


if __name__ == "__main__":
    data1 = FrameData(
        0,
        ImageData(np.zeros((100, 100)), Rect(40, 40, 50, 50)),
        SpeechData("Hello world"),
        Rect(40, 40, 1, 1),
    )
    data2 = FrameData(
        0,
        ImageData(np.zeros((200, 100)), Rect(40, 40, 50, 50)),
        SpeechData("Hello world"),
        Rect(40, 40, 1, 1),
    )
    data3 = FrameData(
        0,
        ImageData(np.zeros((100, 200)), Rect(40, 40, 50, 50)),
        SpeechData("Hello world"),
        Rect(40, 40, 1, 1),
    )

    layout = LayoutGenerator()
    layout.add_frame(data1)
    layout.add_frame(data2)
    layout.add_frame(data1)
    layout.add_frame(data3)
    layout.add_frame(data2)
    layout.add_frame(data1)
    layout.add_frame(data3)

    layout.render_frames_to_image("test.png", 400)
