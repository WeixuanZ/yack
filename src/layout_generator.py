import textwrap
import numpy as np
import drawSvg as draw

from structures import Segment, ImageData, Rect

COMIC_WIDTH = 500
COMIC_MAX_SEGMENT_HEIGHT = 180
COMIC_SPACING_TOLERANCE = 0.2
COMIC_AREA_MIN = 100 * 100
COMIC_PADDING = 5
COMIC_BORDER_WIDTH = 2
BODGE_PT_TO_PX_CONVERSION_X = 6
BODGE_PT_TO_PX_CONVERSION_Y = 10


def suggest_textbox_location(
    normalized_frame_rect: Rect, wrapped_textbox_lines, image: ImageData
):
    width = len(wrapped_textbox_lines[0]) * BODGE_PT_TO_PX_CONVERSION_X
    height = len(wrapped_textbox_lines) * BODGE_PT_TO_PX_CONVERSION_Y

    left_space = image.subject.x
    right_space = image.rect.width - image.subject.x + image.subject.width
    if left_space > right_space:
        return Rect(
            normalized_frame_rect.x, normalized_frame_rect.y + height, width, height
        )
    else:
        return Rect(
            normalized_frame_rect.x, normalized_frame_rect.y + height, width, height
        )


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

    def add_frame(self, frame: Segment):
        self.frames.append(frame)

    def render_frames_to_image(self, file_name: str):
        frame_rects = self.__get_frame_rects_for_rendering(
            COMIC_WIDTH, COMIC_MAX_SEGMENT_HEIGHT
        )

        height = 2000
        ctx = draw.Drawing(
            COMIC_WIDTH + 2 * COMIC_BORDER_WIDTH,
            height,
            origin=(0, 0),
            displayInline=False,
        )
        ctx.append(
            draw.Rectangle(
                COMIC_BORDER_WIDTH,
                COMIC_BORDER_WIDTH,
                COMIC_WIDTH,
                height,
                fill="#fff",
                stroke="#000",
                stroke_width=2 * COMIC_BORDER_WIDTH,
            )
        )
        for rect, frame in zip(frame_rects, self.frames):
            assert isinstance(rect, Rect)
            assert isinstance(frame, Segment)

            normalized_frame_rect = Rect(
                rect.x + COMIC_BORDER_WIDTH,
                height
                - COMIC_BORDER_WIDTH
                - rect.y
                - rect.height,  # Top left coordinate system
                rect.width,
                rect.height,
            )

            # Draw the frame
            ctx.append(
                draw.Image(
                    normalized_frame_rect.x,
                    normalized_frame_rect.y,
                    normalized_frame_rect.width,
                    normalized_frame_rect.height,
                    path=frame.image.uri,
                )
            )
            ctx.append(
                draw.Rectangle(
                    normalized_frame_rect.x,
                    normalized_frame_rect.y,
                    normalized_frame_rect.width,
                    normalized_frame_rect.height,
                    stroke="#000",
                    stroke_width=2 * COMIC_BORDER_WIDTH,
                    fill="rgba(0, 0, 0, 0)",
                )
            )

            # Get the textbox location
            text_box_lines = textwrap.wrap(frame.transcript, 15)
            text_box = suggest_textbox_location(
                normalized_frame_rect, text_box_lines, frame.image
            )
            ctx.append(
                draw.Rectangle(
                    text_box.x,
                    text_box.y,
                    text_box.width,
                    text_box.height,
                    fill="white",
                )
            )

            ctx.append(
                draw.Text(
                    text_box_lines,
                    10,
                    x=text_box.x,
                    y=text_box.y + text_box.height,
                    fill="#000",
                    valign="top",
                )
            )

        ctx.setPixelScale(1)
        ctx.saveSvg(file_name)

    def __get_frame_rects_for_rendering(self, page_width: int, max_height: int):
        frame_rects = []
        unfilled = UnfilledRegion(Rect(0, 0, page_width, max_height))
        for frame in self.frames:
            assert isinstance(frame, Segment)
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
    data1 = Segment(
        0,
        0,
        "Hello world",
        0,
        None,
        0,
        ImageData(np.zeros((200, 100)), Rect(40, 40, 50, 50)),
        Rect(40, 40, 1, 1),
    )
    data2 = Segment(
        0,
        0,
        "Hello world",
        0,
        None,
        0,
        ImageData(np.zeros((100, 100)), Rect(40, 40, 50, 50)),
        Rect(40, 40, 1, 1),
    )
    data3 = Segment(
        0,
        0,
        "Hello world",
        0,
        None,
        0,
        ImageData(np.zeros((100, 200)), Rect(40, 40, 50, 50)),
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
