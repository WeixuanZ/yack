import textwrap

import drawSvg as draw

from structures import ImageData, Rect, Segment

BUBBLE_PADDING = 6
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
            normalized_frame_rect.x + normalized_frame_rect.width - width,
            normalized_frame_rect.y + height,
            width,
            height,
        )


def create_text_bubble(ctx, frame: Segment, normalized_frame_rect: Rect):
    # Get the textbox location
    text_box_lines = textwrap.wrap(frame.transcript, 15)
    text_bb = suggest_textbox_location(
        normalized_frame_rect, text_box_lines, frame.image
    )

    ctx.append(
        draw.Rectangle(
            x=text_bb.x - BUBBLE_PADDING,
            y=text_bb.y - BUBBLE_PADDING,
            rx=5,
            ry=5,
            width=text_bb.width + 2 * BUBBLE_PADDING,
            height=text_bb.height + 2 * BUBBLE_PADDING,
            fill="white",
            stroke="black",
            stroke_width=2,
        )
    )

    ctx.append(
        draw.Text(
            text_box_lines,
            10,
            x=text_bb.x,
            y=text_bb.y + text_bb.height,
            fill="#000",
            valign="top",
        )
    )

    # drawing_obj.append(draw.Ellipse(text_bb.x + (text_bb.width / 2),
    #                                text_bb.y + (text_bb.height / 2),
    #                                (text_bb.width / 2),
    #                                (text_bb.height / 2),
    #                                fill='white',
    #                                stroke="black",
    #                                stroke_width = 2))


if __name__ == "__main__":

    height = 100
    ctx = draw.Drawing(100, height, origin=(0, 0), displayInline=False)
    create_text_bubble(ctx, Rect(10, 10, 70, 40), Rect(0, 50, 50, 50))
    ctx.setPixelScale(1)
    ctx.savePng("example.png")
