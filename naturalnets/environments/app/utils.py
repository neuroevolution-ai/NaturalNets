from naturalnets.environments.app.bounding_box import BoundingBox


import cv2
import numpy as np

from cmath import inf
from typing import List

from naturalnets.environments.app.interfaces import HasBoundingBox

def render_onto_bb(img:np.ndarray, bounding_box:BoundingBox, to_render:np.ndarray) -> np.ndarray:
    """Renders the given to_render onto the given img in bounding_box position.

    Returns:
        np.ndarray: the img containing to_render
    """
    x = bounding_box.x
    y = bounding_box.y
    width = bounding_box.width
    height = bounding_box.height
    img[y:y + height,x:x + width] = to_render
    return img
    
def get_group_bounding_box(group:List[HasBoundingBox]):
    min_x = inf
    min_y = inf
    max_x = 0
    max_y = 0
    for member in group:
        x, y, width, height = member.get_bb().get_as_tuple()
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y
        if x + width > max_x:
            max_x = x + width
        if y + height > max_y:
            max_y = y + height

    width = max_x - min_x
    height = max_y - min_y
    
    return BoundingBox(min_x, min_y, width, height)