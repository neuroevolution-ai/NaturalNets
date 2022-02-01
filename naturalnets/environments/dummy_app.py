from re import I
import numpy as np
import attr
import random
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class DummyAppCfg:
    type: str
    number_time_steps: int


class DummyApp(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):

        self.config = DummyAppCfg(**configuration)

        self.number_checkboxes_horizontal = 5
        self.number_checkboxes_vertical = 5
        self.number_checkboxes = self.number_checkboxes_horizontal * self.number_checkboxes_vertical

        # Initialize Cuda Array for positions of GUI elements
        self.gui_elements_rectangles = np.zeros((self.number_checkboxes, 4))

        self.checkboxes_size = 80
        self.checkboxes_grid_size = 80
        self.checkboxes_border = 0

        # Place all 8 checkboxes in 4 colums and 2 rows
        n = 0
        for i in range(self.number_checkboxes_horizontal):
            for j in range(self.number_checkboxes_vertical):

                x = self.checkboxes_grid_size * i + self.checkboxes_border
                y = self.checkboxes_grid_size * j + self.checkboxes_border

                self.gui_elements_rectangles[n, :] = [x, y, self.checkboxes_size, self.checkboxes_size]
                n += 1

        self.gui_elements_states = np.zeros(self.number_checkboxes)
        self.gui_elements_states[0] = 1

        self.t = 0

    def get_number_inputs(self):
        return self.number_checkboxes

    def get_number_outputs(self):
        return 2

    def reset(self):
        return self.get_observation()

    def step(self, action: np.ndarray):

        click_position = np.zeros(2)

        # Scale actions to click positions
        #random_number = action[threadID+2] * random_normal()
        #click_position[0] = int(0.5 * (action[0] + 1.0) * 400.0)
        #click_position[1] = int(0.5 * (action[1] + 1.0) * 400.0)
    
        click_position[0] = random.randrange(1,400)
        click_position[1] = random.randrange(1,400)

        #checkbox = rand(1:environments.number_checkboxes)
        #click_position[threadID] = environments.gui_elements_rectangles[checkbox, threadID] + 10 

        rew = 0.0

        for i in range(1,self.number_checkboxes):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            if self.is_point_in_rect(click_position[0], click_position[1], rect_x, rect_y, width, height):
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
        pass

    def is_point_in_rect(self, point_x, point_y, rect_x, rect_y, width, height):

        return rect_x <= point_x <= (rect_x + width) and rect_y <= point_y <= (rect_y + height)


# TODO: Do this registration via class decorator
registered_environment_classes['DummyApp'] = DummyApp
