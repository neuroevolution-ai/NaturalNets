import logging
import time
from typing import Optional, Dict

import attr
import cv2
import numpy as np

from naturalnets.enhancers import RandomEnhancer
from naturalnets.environments.gui_app.app_controller import AppController
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.i_environment import IEnvironment, register_environment_class
from naturalnets.tools.utils import rescale_values


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str
    number_time_steps: int


@register_environment_class
class GUIApp(IEnvironment):

    screen_width: int = 448
    screen_height: int = 448

    def __init__(self, configuration: dict, **kwargs):
        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
        t0 = time.time()

        self.config = AppCfg(**configuration)

        self.app_controller = AppController()
        self._initial_state = np.copy(self.app_controller.get_total_state())

        self.t = 0

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
        # Convert from [-1, 1] continuous values to pixel coordinates in [0, screen_width/screen_height]
        click_position_x = int(0.5 * (action[0] + 1.0) * self.screen_width)
        click_position_y = int(0.5 * (action[1] + 1.0) * self.screen_height)

        click_coordinates = np.array([click_position_x, click_position_y])
        self.app_controller.handle_click(click_coordinates)

        self.t += 1

        done = False

        if self.t >= self.config.number_time_steps:
            done = True

        # TODO calculate reward
        return self.get_observation(), 0, done, {}

    def _render_image(self):
        img_shape = (self.screen_width, self.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)

        return image

    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]]):
        image = self._render_image()

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
                    self.screen_width,
                    self.screen_height,
                    color=Color.ORANGE)

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
                self.step(rescale_values(current_action, previous_low=0, previous_high=447, new_low=-1, new_high=1))
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
        return 2

    def reset(self, env_seed: int = None) -> np.ndarray:
        self.get_state()[:] = self._initial_state

        self.t = 0

        return self.get_state()

    def get_observation(self):
        return self.get_state()
