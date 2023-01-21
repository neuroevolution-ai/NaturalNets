import os
from typing import List, Tuple

import cv2
import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Widget
from naturalnets.environments.passlock_app.constants import IMAGES_PATH
from naturalnets.environments.passlock_app.widgets.textfield import Textfield

def draw_rectangle_from_bb(img, bounding_box: BoundingBox, color: Tuple[int, int, int], thickness: int = 2):
    """Draws a rectangle onto the given image in the given bounding box's position.

    Args:
        img (np.ndarray): the image.
        bounding_box (BoundingBox): the bounding box.
        color (Tuple[int,int,int]): the color of the rectangle.
        thickness (int, optional): the thickness of the rectangle. Defaults to 2.
    """
    x, y, width, height = bounding_box.get_as_tuple()
    cv2.rectangle(img, (x, y), (x+width, y+height), color, thickness)

    return img 

def draw_rectangles_around_clickables(lists: List[List[Widget]], to_render: np.ndarray) -> np.ndarray:

    for list in lists:

        for innerlist in list:
            draw_rectangle_from_bb(to_render, innerlist._bounding_box, (0, 255, 0), 2)

def combine_path_for_image(image_path):   
        path = os.path.join(IMAGES_PATH, image_path)
        to_render = cv2.imread(path)
        return to_render

def textfield_check(conditions: List[Textfield]):

        passed = False

        for condition in conditions:
            if(condition.is_selected()):
                passed = True
            else:
                passed = False
                break
        
        return passed