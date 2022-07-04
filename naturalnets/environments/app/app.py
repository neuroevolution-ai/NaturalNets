from cmath import inf
from importlib.util import spec_from_file_location
from re import I
import numpy as np
import attr
import cv2
import time
from naturalnets.environments.app.app_controller import AppController
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.main_window import MainWindow
from naturalnets.environments.app.settings_window import SettingsWindow
from naturalnets.environments.app.state_element import StateElement
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes

from naturalnets.environments.app.exception import InvalidInputError


#TODO
@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    number_time_steps: int
    screen_width: int
    screen_height: int
    interactive: bool
    monkey_tester: bool


class App(IEnvironment):
    def __init__(self, configuration: dict, env_seed: int=None):

        t0 = time.time()

        self.config = AppCfg(**configuration)
        self.action = None

        self.app_controller = AppController()
        self._initial_state = np.copy(self.app_controller.get_app_state())

        t1 = time.time()
        print("App initialized in {0}s.".format(t1-t0))
        print("Total app state length is {0}.".format(self.app_controller._total_state_len))
        print("")

    def step(self, action: np.ndarray):
        #t0 = time.time()

        if self.config.interactive or self.config.monkey_tester:
            self.click_position_x = action[0]
            self.click_position_y = action[1]
        else:
            action = np.tanh(action)

            random_number1 = action[2] * np.random.normal()
            random_number2 = action[3] * np.random.normal()
            self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
            self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        click_coordinates = np.array([self.click_position_x, self.click_position_y])
        #print(click_coordinates)
        self.app_controller.handle_click(click_coordinates)

        #t1 = time.time()

        #print("step took {0}s".format(t1-t0))
        #print("current state:", self.app_controller.get_app_state())

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            #print("click event at ({0},{1})".format(x, y))
            self.action = np.array([x,y,10,10])

    def render(self, click_position:np.ndarray=None):

        img_shape = (self.config.screen_width,self.config.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)
        if click_position is not None:
            cv2.circle(image, (click_position[0], click_position[1]), 4, Color.BLACK.value, -1)

        cv2.imshow("App", image)
        if self.config.interactive:
            # listen for user-click
            cv2.setMouseCallback("App", self.click_event)
            while True:
                ESC_KEY = 27
                input_key = cv2.waitKey(10)
                if input_key == ESC_KEY:
                    # return None as exit "action"
                    cv2.destroyAllWindows()
                    return None
                if self.action is not None:
                    # click sets self.action -> return action
                    action = np.copy(self.action)
                    self.action = None
                    return action
        else:
            cv2.waitKey(1)
        


    def get_number_inputs(self) -> int:
        return 4

    def get_number_outputs(self) -> int:
        return self._state_len

    def reset(self) -> None:
        self._state[:] = self._initial_state