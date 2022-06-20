from cmath import inf
from importlib.util import spec_from_file_location
from re import I
import numpy as np
import attr
import cv2
import time
from naturalnets.environments.app.bounding_box import BoundingBox
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


class App(IEnvironment):
    def __init__(self, configuration: dict, env_seed: int=None):

        t0 = time.time()

        self.config = AppCfg(**configuration)
        self.action = None

        self.main_window = MainWindow()
        self._state_len = self.get_total_state_len(self.main_window)

        self._state = np.zeros(self._state_len, dtype=int)
        self._last_allocated_state_index:int = 0
        self.assign_state(self.main_window)


        self._initial_state = np.copy(self._state)

        t1 = time.time()
        print("App initialized in {0}s.".format(t1-t0))
        print("Total app state length is {0}.".format(self._state_len))
        print("")

    def get_total_state_len(self, stateElement:StateElement) -> int:
        accumulated_len = 0
        for child in stateElement.get_children():
            accumulated_len += self.get_total_state_len(child)
        accumulated_len += stateElement.get_state_len()
        return accumulated_len

    def assign_state(self, stateElement:StateElement) -> None:
        state_len = stateElement.get_state_len()
        state_sector = self.get_next_state_sector(state_len)
        stateElement.assign_state_sector(state_sector)

        for child in stateElement.get_children():
            self.assign_state(child)

    def get_next_state_sector(self, state_len):
        sector_end = self._last_allocated_state_index + state_len
        sector = self._state[self._last_allocated_state_index:sector_end]
        self._last_allocated_state_index = sector_end
        return sector

    def step(self, action: np.ndarray):
        t0 = time.time()

        if self.config.interactive:
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
        self.main_window.handle_click(click_coordinates)

        t1 = time.time()

        #print("step took {0}s".format(t1-t0))
        print("current state:", self._state)

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("click event at ({0},{1})".format(x, y))
            self.action = np.array([x,y,10,10])

    def render(self):
        #TODO: get img depending on current state
        #IMG_PATH:str = 'naturalnets/environments/app/img/'
        #current_img_name:str = self.main_window.get_current_img_name()
        #image = cv2.imread(IMG_PATH + current_img_name)
        #print(current_img_name)

        img_shape = (self.config.screen_width,self.config.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.main_window.render(image)

        if self.config.interactive:
            cv2.imshow("App", image)
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
            cv2.imshow("App", image)
            cv2.waitKey(1)
        


    def get_number_inputs(self) -> int:
        return 4

    def get_number_outputs(self) -> int:
        return self._state_len

    def reset(self) -> None:
        self._state[:] = self._initial_state