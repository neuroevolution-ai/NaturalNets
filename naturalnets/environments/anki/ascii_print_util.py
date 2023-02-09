import cv2
import numpy as np
from typing import Tuple

from PIL import Image, ImageDraw,ImageFont
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import render_onto_bb


class AsciiPrintUtil:

    def print_non_ascii(img: np.ndarray, text: str, bounding_box: BoundingBox, font_size: int, dimension: Tuple[int, int, int]):
        image = np.zeros(dimension, dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
        pil_image = Image.fromarray(image)
        for x in range(pil_image.width):
            for y in range(pil_image.height):
                pil_image.putpixel((x, y), (240,240,240))
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype("arial.ttf", font_size)
        draw.text((5, 5), text, fill = "black", font=font)
        image = np.asarray(pil_image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        render_onto_bb(img, bounding_box, image)
        return img