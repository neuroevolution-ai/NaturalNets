from cmath import inf
from importlib.resources import path as res_path
from typing import List, Tuple, Dict

import cv2
import numpy as np

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.app_components.interfaces import HasBoundingBox


def get_image_path(module: str, file_name: str):
    with res_path(module, file_name) as p:
        return p.__str__()


def render_onto_bb(img: np.ndarray, bounding_box: BoundingBox, to_render: np.ndarray) -> np.ndarray:
    """Renders the given to_render onto the given img in bounding_box position.

    Returns:
        np.ndarray: the img containing to_render
    """

    x = bounding_box.x
    y = bounding_box.y
    width = bounding_box.width
    height = bounding_box.height

    # If the image is the same size as the bounding box and the image does not have square dimensions, we can just replace the image with to_render
    # This sets the shape of the image to the shape of to_render
    if (width == img.shape[0] and height == img.shape[1]):
        img.shape = (height, width, 3)

    img[y:y + height, x:x + width] = to_render

    return img


def get_group_bounding_box(group: List[HasBoundingBox]):
    """Returns the bounding box containing all elements in the given list."""
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


def put_text(img: np.ndarray, text: str, bottom_left_corner: Tuple[int, int], font_scale: float):
    """ Renders the given text onto the given image.

    Args:
        img (np.ndarray): the image.
        text (str): the text.
        bottom_left_corner (Tuple[int,int]): the bottom left corner of the text's position.
        font_scale (float): the factor the text should be scaled by.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_color = Color.BLACK.value
    thickness = 1
    line_type = cv2.LINE_AA
    cv2.putText(img, text, bottom_left_corner, font,
                font_scale, font_color, thickness, line_type)


def generate_reward_mapping_from_template(reward_template: Dict, reward_mapping: Dict, running_index: int = 0):
    """
    Creates a mapping from strings, indicating a specific reward, to an index that can be used to index a NumPy array.

    We use a NumPy array for the reward, where a 0 indicates a reward has not been given, and a 1, that a reward has
    been given. To index that array we use the reward_mapping dict to have a better overview of the array. Previously
    using a reward dict, and making diffs between that dict did not work, as it is computationally inefficient, compared
    to comparing NumPy arrays.

    :param reward_template: The reward_template of the RewardElement, see more in the RewardElement class
    :param reward_mapping: An already created reward_mapping, because the function is also used recursively
    :param running_index: Currently free index in the array, will be incremented each time an index is mapped
    :return: The finished reward_mapping, a dict that maps reward strings to indices in the reward_array NumPy array
    """
    for k, v in reward_template.items():
        if isinstance(v, dict):
            reward_mapping[k] = {}
            _, running_index = generate_reward_mapping_from_template(
                v, reward_mapping[k], running_index)
        elif isinstance(v, list):
            reward_mapping[k] = {}
            for list_entry in v:
                reward_mapping[k][list_entry] = running_index
                running_index += 1
        else:
            reward_mapping[k] = running_index
            running_index += 1

    return reward_mapping, running_index
