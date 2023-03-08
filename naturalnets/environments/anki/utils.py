from typing import Tuple
import cv2
import numpy as np
from naturalnets.environments.anki.constants import ANKI_COLOR
from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.app_components.utils import render_onto_bb
from PIL import Image, ImageDraw, ImageFont


def print_non_ascii(img: np.ndarray, text: str, bounding_box: BoundingBox, font_size: int, dimension: Tuple[int, int, int]):
    to_render_image = np.zeros(dimension, dtype=np.uint8)
    to_render_image = cv2.cvtColor(to_render_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(to_render_image)
    for x in range(pil_image.width):
        for y in range(pil_image.height):
            pil_image.putpixel((x, y), ANKI_COLOR)
    draw = ImageDraw.Draw(pil_image)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((5, 5), text, fill="black", font=font)
    image = np.asarray(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    render_onto_bb(img, bounding_box, image)
    return img


"""
    Calculate the clickable area of the table depending on the number of
    current decks/profiles.
"""


def calculate_current_bounding_box(x_position: int, y_position: int, item_height: int, item_width: int, item_number: int):
    upper_left_point = (x_position, y_position)
    length = item_height * item_number
    current_bounding_box = BoundingBox(
        upper_left_point[0], upper_left_point[1], item_width, length)
    return current_bounding_box
