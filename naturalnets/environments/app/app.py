"""Contains the App."""

import time
import cv2
import numpy as np
import attr
from naturalnets.environments.app.app_controller import AppController
from naturalnets.environments.app.enums import Color
from naturalnets.environments.i_environment import IEnvironment


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
        self._initial_state = np.copy(self.app_controller.get_total_state())

        self.action_x = 0
        self.action_y = 0

        self.random_number_x = 0
        self.random_number_y = 0

        self.click_position_x = 0
        self.click_position_y = 0

        t1 = time.time()
        print(f"App initialized in {t1-t0}s.")
        print(f"Total app state length is {self.app_controller._total_state_len}.")
        print("")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):

        if self.config.interactive or self.config.monkey_tester:
            self.click_position_x = action[0]
            self.click_position_y = action[1]
        else:
            action = np.tanh(action)

            random_number1 = action[2] * np.random.normal()
            random_number2 = action[3] * np.random.normal()
            self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1)
                                                * self.config.screen_width)
            self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2)
                                                * self.config.screen_height)

        click_coordinates = np.array([self.click_position_x, self.click_position_y])
        self.app_controller.handle_click(click_coordinates)


    def click_event(self, event, x, y, flags, params):
        """Sets action when cv2 mouse-callback is detected."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.action = np.array([x,y,10,10])

    def render(self, click_position:np.ndarray=None):
        """Renders the app depending on the apps configuration (interactive vs. other)"""

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
        return self.app_controller.get_total_state_len()

    def reset(self) -> None:
        self.get_state()[:] = self._initial_state

    def get_observation(self):
        return self.get_state()
