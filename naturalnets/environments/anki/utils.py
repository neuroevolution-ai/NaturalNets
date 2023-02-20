from typing import Tuple
import cv2
import numpy as np
from naturalnets.environments.anki.constants import ANKI_COLOR, FONTS_PATH 
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.utils import render_onto_bb
from PIL import Image, ImageDraw, ImageFont

def print_non_ascii(img: np.ndarray, text: str, bounding_box: BoundingBox, font_size: int,
                        dimension: Tuple[int, int, int]):
        image = np.zeros(dimension, dtype=np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)
        for x in range(pil_image.width):
            for y in range(pil_image.height):
                pil_image.putpixel((x, y), ANKI_COLOR)
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype(FONTS_PATH, font_size)
        draw.text((5, 5), text, fill="black", font=font)
        image = np.asarray(pil_image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        render_onto_bb(img, bounding_box, image)
        return img
