import drawSvg as draw

from structures import Rect, Segment
from text_box import create_text_bubble

COMIC_WIDTH = 450
COMIC_MAX_SEGMENT_HEIGHT = 180
COMIC_SPACING_TOLERANCE = 0.2
COMIC_AREA_MIN = 100 * 100
COMIC_PADDING = 8
COMIC_BORDER_WIDTH = 2


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
            )
        )
        for rect, frame in zip(frame_rects, self.frames):
            assert isinstance(rect, Rect)
            assert isinstance(frame, Segment)

            normalized_frame_rect = Rect(
                rect.x + COMIC_BORDER_WIDTH + COMIC_PADDING,
                height
                - COMIC_BORDER_WIDTH
                - COMIC_PADDING
                - rect.y
                - rect.height,  # Top left coordinate system
                rect.width - 2 * COMIC_PADDING,
                rect.height - 2 * COMIC_PADDING,
            )

            # Draw the frame
            ctx.append(
                draw.Image(
                    normalized_frame_rect.x,
                    normalized_frame_rect.y,
                    normalized_frame_rect.width,
                    normalized_frame_rect.height,
                    path=f"data:image/png;base64,{frame.image.b64png.decode('ascii')}",
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

            if frame.transcript:
                create_text_bubble(ctx, frame, normalized_frame_rect)

        ctx.setPixelScale(1)
        ctx.saveSvg(file_name)

    def __get_frame_rects_for_rendering(self, page_width: int, max_height: int):
        frame_rects = []
        unfilled = UnfilledRegion(Rect(0, 0, page_width, max_height))
        for frame in self.frames:
            assert isinstance(frame, Segment)

            frame_rect = unfilled.claim_chunk(frame.image.rect.aspect)
            if not frame_rect:
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
