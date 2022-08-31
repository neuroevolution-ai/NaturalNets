import logging
import time

import attr
import cv2
import numpy as np

from naturalnets.environments.app.app_controller import AppController
from naturalnets.environments.app.enums import Color
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str
    number_time_steps: int
    interactive: bool # true = no agent, clicks generated by a person
    monkey_tester: bool # set this to true to let a simple monkey tester generate actions (clicks)


class App(IEnvironment):
    SCREEN_WIDTH: int = 448
    SCREEN_HEIGHT: int = 448

    def __init__(self, configuration: dict, **kwargs):
        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
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

        logging.debug(f"App initialized in {t1 - t0}s.")
        logging.debug(f"Total app state length is {len(self._initial_state)}.")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):

        if self.config.interactive or self.config.monkey_tester:
            self.click_position_x = action[0]
            self.click_position_y = action[1]
        else:
            action = np.tanh(action)

            # actions[2] and action[3] represent click-position uncertainty
            random_number1 = action[2] * np.random.normal()
            random_number2 = action[3] * np.random.normal()
            self.click_position_x = int(
                0.5 * (action[0] + 1.0 + random_number1) * self.SCREEN_WIDTH
            )
            self.click_position_y = int(
                0.5 * (action[1] + 1.0 + random_number2) * self.SCREEN_HEIGHT
            )

        click_coordinates = np.array([self.click_position_x, self.click_position_y])
        self.app_controller.handle_click(click_coordinates)

    def click_event(self, event, x, y, flags, params):
        """Sets action when cv2 mouse-callback is detected. Only for interactive mode."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # values for action[2] and action [3] do not matter here, 
            # since they are not used in interactive mode
            self.action = np.array([x, y, 0, 0])

    def render(self, click_position: np.ndarray = None):
        """Renders the app depending on the apps' configuration (interactive vs. other)"""

        img_shape = (self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)
        if click_position is not None:
            # Thickness=-1 will fill the circle shape with the specified color
            cv2.circle(image, (click_position[0], click_position[1]), radius=4, color=Color.BLACK.value, thickness=-1)

        cv2.imshow("App", image)
        if self.config.interactive:
            # Listen for user-click
            cv2.setMouseCallback("App", self.click_event)
            while True:
                input_key = cv2.waitKey(10)

                # Keycode 27 is the ESC key
                if input_key == 27:
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

    # TODO change number_inputs and number_outputs as these are false, but wait for the GitHub
    #   PR review comment to be resolved

    def get_number_inputs(self) -> int:
        return self.app_controller.get_total_state_len()

    def get_number_outputs(self) -> int:
        return 4

    def reset(self) -> np.ndarray:
        self.get_state()[:] = self._initial_state
        return self.get_state()

    def get_observation(self):
        return self.get_state()


registered_environment_classes["GUIApp"] = App
