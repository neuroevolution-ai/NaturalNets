from re import I
import numpy as np
import attr
import cv2
import random
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes


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

    def __init__(self, env_seed: int, configuration: dict):

        self.config = DummyAppCfg(**configuration)
        self.number_buttons = self.config.number_buttons_horizontal * self.config.number_buttons_vertical

        # Initialize Cuda Array for positions of GUI elements
        self.gui_elements_rectangles = np.zeros((self.number_buttons, 4), dtype=np.uint32)

        grid_size_horizontal = self.config.screen_width / self.config.number_buttons_horizontal
        grid_size_vertical = self.config.screen_height / self.config.number_buttons_vertical
        border_horizontal = (grid_size_horizontal - self.config.buttons_size_horizontal)/2
        border_vertical = (grid_size_vertical - self.config.buttons_size_vertical)/2

        # Place all 8 checkboxes in 4 colums and 2 rows
        n = 0
        for i in range(self.config.number_buttons_horizontal):
            for j in range(self.config.number_buttons_vertical):

                x = grid_size_horizontal * i + border_horizontal
                y = grid_size_vertical * j + border_vertical

                self.gui_elements_rectangles[n, :] = [x, y, self.config.buttons_size_horizontal, self.config.buttons_size_vertical]
                n += 1

        self.action_x = 0
        self.action_y = 0

        self.random_number_x = 0
        self.random_number_y = 0

        self.click_position_x = 0
        self.click_position_y = 0

        self.gui_elements_states = np.zeros(self.number_buttons)
        self.gui_elements_states[0] = 1

        self.t = 0

    def get_number_inputs(self):
        return self.number_buttons

    def get_number_outputs(self):
        return 4

    def reset(self):
        return self.get_observation()

    def step(self, action: np.ndarray):

        random_number1 = action[2] * np.random.normal()
        random_number2 = action[3] * np.random.normal()
        self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
        self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        self.action = action

        #self.click_position_x = random.randint(1, self.config.screen_width)
        #self.click_position_y = random.randint(1, self.config.screen_height)

        #button = random.randrange(self.number_buttons)
        #self.click_position_x = self.gui_elements_rectangles[button, 0]
        #self.click_position_y = self.gui_elements_rectangles[button, 1]

        rew = 0.0

        for i in range(1, self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            if self.is_point_in_rect(self.click_position_x, self.click_position_y, rect_x, rect_y, width, height):
                if self.gui_elements_states[i] == 0 and self.gui_elements_states[i-1] == 1:
                    rew += 1.0
                    self.gui_elements_states[i] = 1

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

    def render(self):

        red = (0, 0, 255)
        green = (0, 255, 0)
        black = (0, 0, 0)
        blue = (255, 0, 0)
        orange = (0, 88, 255)

        # Initialize image with white background
        image = 255 * np.ones(shape=[self.config.screen_width, self.config.screen_height, 3], dtype=np.uint8)

        # Buttons
        for i in range(self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            point1 = (rect_x, rect_y)
            point2 = (rect_x + width, rect_y + height)

            if self.gui_elements_states[i] == 0:
                color = blue
            else:
                color = green

            image = cv2.rectangle(image, point1, point2, color, -1)
            image = cv2.rectangle(image, point1, point2, black, 1)

        # Action position
        action_position_x = int(0.5 * (self.action[0] + 1.0) * self.config.screen_width)
        action_position_y = int(0.5 * (self.action[1] + 1.0) * self.config.screen_height)
        image = cv2.circle(image, (action_position_x, action_position_y), 2, orange, -1)

        # Action distribution as ellipse
        action_distribution_x = abs(int(0.5 * self.action[2] * self.config.screen_width))
        action_distribution_y = abs(int(0.5 * self.action[3] * self.config.screen_height))
        image = cv2.ellipse(image, (action_position_x, action_position_y), (action_distribution_x, action_distribution_y), 0, 0, 360, orange, 1)

        # Click position
        image = cv2.circle(image, (self.click_position_x, self.click_position_y), 3, red, -1)

        cv2.imshow("Dummy App", cv2.resize(image, (self.config.screen_width, self.config.screen_height)))
        cv2.waitKey(1)

    def is_point_in_rect(self, point_x, point_y, rect_x, rect_y, width, height):

        return rect_x <= point_x <= (rect_x + width) and rect_y <= point_y <= (rect_y + height)


# TODO: Do this registration via class decorator
registered_environment_classes['DummyApp'] = DummyApp
