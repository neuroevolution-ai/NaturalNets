from naturalnets.environments.app.bounding_box import BoundingBox


import cv2
import numpy as np

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