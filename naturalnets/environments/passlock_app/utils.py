from typing import Tuple

import cv2
from naturalnets.environments.gui_app.bounding_box import BoundingBox

def draw_rectangle_from_bb(img, bounding_box: BoundingBox, color: Tuple[int, int, int], thickness: int = 2):
    """Draws a rectangle onto the given image in the given bounding box's position.

    Args:
        img (np.ndarray): the image.
        bounding_box (BoundingBox): the bounding box.
        color (Tuple[int,int,int]): the color of the rectangle.
        thickness (int, optional): the thickness of the rectangle. Defaults to 2.
    """
    x, y, width, height = bounding_box.get_as_tuple()
    cv2.rectangle(img, (bounding_box.x1, bounding_box.y1), (bounding_box.x2, bounding_box.y2), color, thickness)

    return img 