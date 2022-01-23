import drawSvg as draw
from structures import Rect

BUBBLE_PADDING = 6


def create_text_bubble(drawing_obj, text_bb: Rect, speaker_bb: Rect):
    drawing_obj.append(
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
