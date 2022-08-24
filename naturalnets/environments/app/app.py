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
    screen_width: int
    screen_height: int


class App(IEnvironment):
    def __init__(self, configuration: dict, **kwargs):
        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
        t0 = time.time()

        self.config = AppCfg(**configuration)

        self.app_controller = AppController()
        self._initial_state = np.copy(self.app_controller.get_total_state())

        self.action_x = 0
        self.action_y = 0

        self.random_number_x = 0
        self.random_number_y = 0

        self.click_position_x = 0
        self.click_position_y = 0

        # Used for the interactive mode, in which the user can click through an OpenCV rendered
        # version of the app
        self.window_name = "App"
        self.action = None
        self.clicked = False

        t1 = time.time()

        logging.debug(f"App initialized in {t1 - t0}s.")
        logging.debug(f"Total app state length is {len(self._initial_state)}.")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):
        assert np.min(action) >= -1 and np.max(action) <= 1, ("Action coming from the brain is not in the [-1, 1] "
                                                              "value range.")

        random_number1 = action[2] * np.random.normal()
        random_number2 = action[3] * np.random.normal()
        self.click_position_x = int(
            0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width
        )
        self.click_position_y = int(
            0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height
        )

        click_coordinates = np.array([self.click_position_x, self.click_position_y])
        self.app_controller.handle_click(click_coordinates)

    def _render_image(self):
        img_shape = (self.config.screen_width, self.config.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)

        return image

    def render(self):
        image = self._render_image()
        cv2.imshow(self.window_name, image)
        cv2.waitKey(1)

    def click_event(self, event, x, y, _flags, _params):
        """Sets action when cv2 mouse-callback is detected, i.e. user has clicked."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.action = np.array([x, y])
            self.clicked = True

    def interactive_mode(self):
        # Create the window here first, so that the callback can be registered
        # The callback simply registers the clicks of a user
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.click_event)

        while True:
            current_action = None
            if self.clicked:
                current_action = self.action
                self.step(self.action)
                self.clicked = False

            image = self._render_image()

            if current_action is not None:
                # Draw the position of the click as a black circle;
                # thickness=-1 will fill the circle shape with the specified color
                cv2.circle(
                    image,
                    (current_action[0], current_action[1]), radius=4, color=Color.BLACK.value, thickness=-1
                )

            cv2.imshow(self.window_name, image)

            while True:
                # Waits 50ms for a key press (notice that this does not include mouse clicks,
                # therefore we use the callback method for the clicks)
                key = cv2.waitKey(50)

                # Keycode 27 is the ESC key
                if key == 27:
                    cv2.destroyAllWindows()
                    return

                if self.clicked:
                    # The user clicked, thus use the position for a step() and render the new image
                    break

    def get_number_inputs(self) -> int:
        return self.app_controller.get_total_state_len()

    def get_number_outputs(self) -> int:
        return 4

    def reset(self, env_seed: int = None) -> np.ndarray:
        self.get_state()[:] = self._initial_state
        return self.get_state()

    def get_observation(self):
        return self.get_state()


registered_environment_classes["GUIApp"] = App
