import math
from cmath import inf
from typing import Dict

import cv2
import numpy as np
from attrs import define, field, validators
from numpy.random import default_rng

from naturalnets.enhancers import RandomEnhancer
from naturalnets.environments.i_environment import IEnvironment, register_environment_class

# Variables for rendering the DummyApp
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
BLUE = (255, 0, 0)
ORANGE = (0, 88, 255)

FONT = cv2.FONT_HERSHEY_PLAIN
FONT_SCALE = 1
THICKNESS = 1

# Variables concerning the inner workings of the environment
FIXED_ENV_SEED = 0


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class DummyAppCfg:
    type: str = field(validator=validators.instance_of(str))
    number_time_steps: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    screen_width: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    screen_height: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    number_button_columns: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    number_button_rows: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    button_width: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    button_height: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    force_consecutive_click_order: bool = field(default=True, validator=[validators.instance_of(int)])
    fixed_env_seed: bool = field(validator=[validators.instance_of(bool)])


@register_environment_class
class DummyApp(IEnvironment):

    def __init__(self, configuration: dict, **kwargs):
        self.config = DummyAppCfg(**configuration)
        self.number_buttons = self.config.number_button_columns * self.config.number_button_rows

        # Contains the x and y coordinates of the upper left point of the button's rectangle
        self.button_rectangle_positions = np.zeros((self.number_buttons, 2), dtype=np.uint32)

        # Width and height of one cell of the button grid
        self.grid_cell_horizontal_size = self.config.screen_width // self.config.number_button_columns
        self.grid_cell_vertical_size = self.config.screen_height // self.config.number_button_rows

        err = "Grid cells are less than 1 pixel large, increase screen width and/or height, or decrease button sizes."
        assert self.grid_cell_horizontal_size > 1 and self.grid_cell_vertical_size > 1, err

        # Considering the upper left point of one cell of the button grid, calculate the offset in x and y direction,
        # of that point, such that the button rectangle is in the middle of that cell.
        # -> Calculate the total space in the grid, then half it to center the button rectangle
        self.grid_cell_horizontal_offset = (self.grid_cell_horizontal_size - self.config.button_width) // 2
        self.grid_cell_vertical_offset = (self.grid_cell_vertical_size - self.config.button_height) // 2

        err = ("The chosen number of buttons do not fit into the button grid. Consider increasing the\n"
               "screen size, decreasing the button sizes, or decreasing the amount of button rows and/or columns.")
        assert self.grid_cell_horizontal_offset >= 0 and self.grid_cell_vertical_offset >= 0, err

        self.rng = default_rng()
        self.window_name = "DummyApp"

        self.buttons = None

        self.click_position_x = 0
        self.click_position_y = 0

        self.button_states = np.zeros(self.number_buttons, dtype=np.uint8)

        self.t = 0

    def get_number_inputs(self):
        return self.number_buttons

    def get_number_outputs(self):
        return 2

    def reset(self, env_seed: int = None):
        if self.config.fixed_env_seed:
            self.rng = default_rng(seed=FIXED_ENV_SEED)
        else:
            self.rng = default_rng(seed=env_seed)

        self.buttons = np.arange(self.number_buttons)
        self.rng.shuffle(self.buttons)

        # Place the shuffled buttons on the grid
        n = 0
        for j in range(self.config.number_button_rows):
            for i in range(self.config.number_button_columns):
                x = self.grid_cell_horizontal_size * i + self.grid_cell_horizontal_offset
                y = self.grid_cell_vertical_size * j + self.grid_cell_vertical_offset

                button = self.buttons[n]

                self.button_rectangle_positions[button, :] = [x, y]
                n += 1

        self.click_position_x = 0
        self.click_position_y = 0

        self.button_states = np.zeros(self.number_buttons, dtype=np.uint8)

        self.t = 0

        return self.get_observation()

    def step(self, action: np.ndarray):
        # Convert from [-1, 1] continuous values to pixel coordinates in [0, screen_width/screen_height]
        self.click_position_x = int(0.5 * (action[0] + 1.0) * self.config.screen_width)
        self.click_position_y = int(0.5 * (action[1] + 1.0) * self.config.screen_height)

        # Find chosen button based on mouse click position
        minimal_distance = inf
        button = 0
        for i in range(self.number_buttons):

            # Upper left point of the corresponding button's rectangle
            rect_x = self.button_rectangle_positions[i, 0]
            rect_y = self.button_rectangle_positions[i, 1]

            distance = self.rect_distance(self.click_position_x, self.click_position_y, rect_x, rect_y,
                                          self.config.button_width, self.config.button_height)

            if distance < minimal_distance:
                minimal_distance = distance
                button = i

                if distance == 0.0:
                    break

        return self.step_widget(button)

    def step_widget(self, widget_id: int):
        button = widget_id
        rew = 0.0

        if self.config.force_consecutive_click_order:
            if button == 0:
                if self.button_states[0] == 0:
                    rew += 1.0
                    self.button_states[0] = 1
            else:
                if self.button_states[button] == 0 and self.button_states[button - 1] == 1:
                    rew += 1.0
                    self.button_states[button] = 1
        else:
            if self.button_states[button] == 0:
                rew += 1.0
                self.button_states[button] = 1

        self.t += 1

        done = False
        if self.t >= self.config.number_time_steps:
            done = True

        ob = self.get_observation()
        info = {"action": button}

        return ob, rew, done, info

    def get_observation(self):
        return self.button_states

    def get_observation_dict(self):

        observation = dict()
        observation["pressed buttons"] = list()

        for i in range(len(self.button_states)):
            if self.button_states[i] == 1:
                observation["pressed buttons"].append(i)

        return observation

    def _render_image(self):
        image = np.zeros((self.config.screen_height, self.config.screen_width, 3), dtype=np.uint8)
        image[:, :, :] = 255

        # Draw button rectangles
        for i in range(self.number_buttons):
            rect_x = self.button_rectangle_positions[i, 0]
            rect_y = self.button_rectangle_positions[i, 1]

            point_1 = (rect_x, rect_y)
            point_2 = (rect_x + self.config.button_width, rect_y + self.config.button_height)

            if self.button_states[i] == 0:
                color = RED
            else:
                color = GREEN

            image = cv2.rectangle(image, point_1, point_2, color, thickness=1)

            button_text = str(i)
            text_width, text_height = cv2.getTextSize(button_text, fontFace=FONT, fontScale=FONT_SCALE,
                                                      thickness=THICKNESS)[0]

            # Go from top left point of the button box to the middle of the box and then move back half of the text
            # width, s.t. the text is centered in the button
            text_point_x = int(rect_x + self.config.button_width / 2 - text_width / 2)
            text_point_y = int(rect_y + self.config.button_height / 2 + text_height / 2)

            image = cv2.putText(image, str(i), (text_point_x, text_point_y), cv2.FONT_HERSHEY_PLAIN,
                                fontScale=FONT_SCALE, color=BLACK, thickness=THICKNESS, lineType=cv2.LINE_AA)

        return image

    def render(self, enhancer_info: Dict = None):

        image = self._render_image()

        # Draw click areas, i.e. cells of the grid in which the buttons reside
        for j in range(self.config.number_button_rows):
            for i in range(self.config.number_button_columns):
                x = self.grid_cell_horizontal_size * i
                y = self.grid_cell_vertical_size * j

                image = cv2.rectangle(
                    image,
                    (x, y),
                    (x + self.grid_cell_horizontal_size, y + self.grid_cell_vertical_size),
                    GREY,
                    thickness=1
                )

        if enhancer_info is not None:
            try:
                random_enhancer_info = enhancer_info["random_enhancer_info"]
            except KeyError:
                # Enhancer info other than from the random enhancer is not (currently) visualized
                pass
            else:
                image = RandomEnhancer.render_visualization_ellipses(
                    image,
                    random_enhancer_info,
                    self.config.screen_width,
                    self.config.screen_height,
                    color=ORANGE
                )

        # Click position
        image = cv2.circle(image, (self.click_position_x, self.click_position_y), radius=3, color=BLUE, thickness=-1)

        cv2.imshow(self.window_name, image)
        cv2.waitKey(1)

    def get_window_name(self):
        return self.window_name

    def get_screen_size(self):
        assert self.config.screen_width == self.config.screen_height
        return self.config.screen_width

    @staticmethod
    def is_point_in_rect(point_x, point_y, rect_x, rect_y, width, height):
        return rect_x <= point_x <= (rect_x + width) and rect_y <= point_y <= (rect_y + height)

    @staticmethod
    def rect_distance(point_x, point_y, rect_x, rect_y, width, height):
        # https://stackoverflow.com/questions/5254838/calculating-distance-between-a-point-and-a-rectangular-box-nearest-point
        dx = max(rect_x - point_x, 0, point_x - rect_x - width)
        dy = max(rect_y - point_y, 0, point_y - rect_y - height)

        return math.sqrt(dx * dx + dy * dy)
