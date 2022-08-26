import math
from cmath import inf
from typing import Dict

import attr
import cv2
import numpy as np

from naturalnets.enhancers import RandomEnhancer
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes

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


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class DummyAppCfg:
    type: str
    number_time_steps: int
    screen_width: int
    screen_height: int
    number_buttons_horizontal: int
    number_buttons_vertical: int
    buttons_size_horizontal: int
    buttons_size_vertical: int


class DummyApp(IEnvironment):

    def __init__(self, configuration: dict):

        self.config = DummyAppCfg(**configuration)
        self.number_buttons = self.config.number_buttons_horizontal * self.config.number_buttons_vertical

        # Initialize Cuda Array for positions of GUI elements
        self.gui_elements_rectangles = np.zeros((self.number_buttons, 4), dtype=np.uint32)

        self.grid_size_horizontal = self.config.screen_width / self.config.number_buttons_horizontal
        self.grid_size_vertical = self.config.screen_height / self.config.number_buttons_vertical
        border_horizontal = (self.grid_size_horizontal - self.config.buttons_size_horizontal)/2
        border_vertical = (self.grid_size_vertical - self.config.buttons_size_vertical)/2

        self.buttons = [12, 6, 16, 9, 0, 2, 11, 7, 13, 8, 22, 1, 23, 17, 19, 24, 10, 20, 4, 21, 15, 18, 14, 5, 3]

        # Place all 8 checkboxes in 4 colums and 2 rows
        n = 0
        for i in range(self.config.number_buttons_vertical):
            for j in range(self.config.number_buttons_horizontal):

                x = self.grid_size_horizontal * i + border_horizontal
                y = self.grid_size_vertical * j + border_vertical

                button = self.buttons[n]

                self.gui_elements_rectangles[button, :] = [x, y, self.config.buttons_size_horizontal, self.config.buttons_size_vertical]
                n += 1

        self.click_position_x = 0
        self.click_position_y = 0

        self.gui_elements_states = np.zeros(self.number_buttons)

        self.t = 0

    def get_number_inputs(self):
        return self.number_buttons

    def get_number_outputs(self):
        return 2

    def reset(self, env_seed: int = None):
        return self.get_observation()

    def step(self, action: np.ndarray):
        assert np.min(action) >= -1 and np.max(action) <= 1, ("Action coming from the brain is not in the [-1, 1] "
                                                              "value range.")

        # Convert from [-1, 1] continuous values to pixel coordinates
        self.click_position_x = int(0.5 * (action[0] + 1.0) * self.config.screen_width)
        self.click_position_y = int(0.5 * (action[1] + 1.0) * self.config.screen_height)

        # random_number1 = action[2] * np.random.normal()
        # random_number2 = action[3] * np.random.normal()
        # self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
        # self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        # self.action = action

        #self.click_position_x = random.randint(1, self.config.screen_width)
        #self.click_position_y = random.randint(1, self.config.screen_height)

        #button = random.randrange(self.number_buttons)
        #self.click_position_x = self.gui_elements_rectangles[button, 0] + 1
        #self.click_position_y = self.gui_elements_rectangles[button, 1] + 1

        rew = 0.0

        # Find chosen button based on mouse click position
        minimal_distance = inf
        button = 0
        for i in range(self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            distance = self.rect_distance(self.click_position_x, self.click_position_y, rect_x, rect_y, width, height)

            if distance < minimal_distance:
                minimal_distance = distance
                button = i

            if distance < 0.0001:
                break

        if button == 0:
            if self.gui_elements_states[0] == 0:
                rew += 1.0
                self.gui_elements_states[0] = 1
        else:
            if self.gui_elements_states[button] == 0 and self.gui_elements_states[button-1] == 1:
                rew += 1.0
                self.gui_elements_states[button] = 1

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        ob = self.get_observation()
        info = dict()

        return ob, rew, done, info

    def get_observation(self):
        return self.gui_elements_states

    def render(self, enhancer_info: Dict = None):
        image = np.zeros((self.config.screen_height, self.config.screen_width, 3), dtype=np.uint8)
        image[:, :, :] = 255

        # Buttons
        for i in range(self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            point1 = (rect_x, rect_y)
            point2 = (rect_x + width, rect_y + height)

            if self.gui_elements_states[i] == 0:
                color = RED
            else:
                color = GREEN

            image = cv2.rectangle(image, point1, point2, color, 1)

            button_text = str(i)
            text_width, text_height = cv2.getTextSize(button_text, fontFace=FONT, fontScale=FONT_SCALE,
                                                      thickness=THICKNESS)[0]

            # Go from top left point of the button box to the middle of the box and then move back half of the text
            # width, s.t. the text is centered in the button
            text_point_x = int(rect_x + width / 2 - text_width / 2)
            text_point_y = int(rect_y + height / 2 + text_height / 2)

            image = cv2.putText(image, str(i), (text_point_x, text_point_y), cv2.FONT_HERSHEY_PLAIN, fontScale=1,
                                color=BLACK, thickness=1, lineType=cv2.LINE_AA)

        # Click areas
        for i in range(self.config.number_buttons_vertical):
            for j in range(self.config.number_buttons_horizontal):
                x = int(self.grid_size_horizontal * i)
                y = int(self.grid_size_vertical * j)
                width = int(self.grid_size_horizontal)
                height = int(self.grid_size_vertical)

                image = cv2.rectangle(image, (x, y), (x + width, y + height), GREY, thickness=1)

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

        cv2.imshow("Dummy App", image)
        cv2.waitKey(1)

    def is_point_in_rect(self, point_x, point_y, rect_x, rect_y, width, height):

        return rect_x <= point_x <= (rect_x + width) and rect_y <= point_y <= (rect_y + height)

    # https://stackoverflow.com/questions/5254838/calculating-distance-between-a-point-and-a-rectangular-box-nearest-point
    def rect_distance(self, point_x, point_y, rect_x, rect_y, width, height):
        dx = max(rect_x - point_x, 0, point_x - rect_x - width)
        dy = max(rect_y - point_y, 0, point_y - rect_y - height)

        return math.sqrt(dx*dx + dy*dy)


# TODO: Do this registration via class decorator
registered_environment_classes["DummyApp"] = DummyApp
