import drawSvg as draw
from structures import Rect

def create_text_bubble(drawing_obj, text_bb: Rect, speaker_bb: Rect):
    drawing_obj.append(draw.Rectangle(
                                    x = text_bb.x,
                                    y = text_bb.y,
                                    rx = 5,
                                    ry = 5,
                                    width = text_bb.width,
                                    height = text_bb.height, 
                                    fill = 'white', 
                                    stroke = 'black', 
                                    stroke_width = 2
                                    ))
    
    #drawing_obj.append(draw.Ellipse(text_bb.x + (text_bb.width / 2),
    #                                text_bb.y + (text_bb.height / 2),
    #                                (text_bb.width / 2),
    #                                (text_bb.height / 2), 
    #                                fill='white', 
    #                                stroke="black",
    #                                stroke_width = 2))
    
    #drawing_obj.setPixelScale(1)
    #drawing_obj.savePng('example.png')


if __name__ == "__main__":
    
        height = 100
        ctx = draw.Drawing(
            100, height, origin=(0, 0), displayInline=False
        )
        create_text_bubble(ctx, Rect(10, 10, 70, 40), Rect(0, 50, 50, 50))