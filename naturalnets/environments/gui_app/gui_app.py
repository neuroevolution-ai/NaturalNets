import enum
import logging
import time
from typing import Optional, Dict, List

import attrs
from attrs import field, validators
import cv2
import numpy as np

from naturalnets.enhancers import RandomEnhancer
from naturalnets.environments.gui_app.app_controller import AppController
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.i_environment import IEnvironment, register_environment_class
from naturalnets.tools.utils import rescale_values


class FakeBugOptions(enum.Enum):
    pass


@attrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str
    number_time_steps: int
    include_fake_bug: bool = field(validator=validators.instance_of(bool))
    fake_bugs: List[str] = field(default=None,
                                 validator=[validators.optional(validators.in_([opt.value for opt in FakeBugOptions]))])

    def __attrs_post_init__(self):
        if self.include_fake_bug:
            assert self.fake_bugs is not None and len(self.fake_bugs) > 0, ("'include_fake_bug' is set to True, please "
                                                                            "provide a list of fake bugs using 'fake_"
                                                                            "bugs'.")


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

        self.t = 0

        # Used for the interactive mode, in which the user can click through an OpenCV rendered
        # version of the app
        self.window_name = "App"
        self.action = None
        self.clicked = False

        t1 = time.time()

        logging.debug(f"App initialized in {t1 - t0}s.")
        logging.debug(f"Total app state length is {self.app_controller.get_total_state_len()}.")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):
        # Convert from [-1, 1] continuous values to pixel coordinates in [0, screen_width/screen_height]
        click_position_x = int(0.5 * (action[0] + 1.0) * self.screen_width)
        click_position_y = int(0.5 * (action[1] + 1.0) * self.screen_height)

        click_coordinates = np.array([click_position_x, click_position_y])
        rew = self.app_controller.handle_click(click_coordinates)

        # Give a reward equal to the number of time steps at the beginning to avoid negative rewards
        if self.t == 0:
            rew += self.config.number_time_steps

        # Give a negative reward of 1 for each timestep
        rew -= 1

        done = False

        self.t += 1

        if self.t >= self.config.number_time_steps:
            done = True

        return self.get_observation(), rew, done, {}

    def _render_image(self):
        img_shape = (self.screen_width, self.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)

        return image

    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]] = None):
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

    def interactive_mode(self, print_reward: bool = False):
        # Create the window here first, so that the callback can be registered
        # The callback simply registers the clicks of a user
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.click_event)

        while True:
            current_action = None
            if self.clicked:
                current_action = self.action
                _, rew, _, _ = self.step(rescale_values(current_action, previous_low=0, previous_high=447, new_low=-1,
                                                        new_high=1))
                self.clicked = False

                if print_reward:
                    print(f"Reward: {rew}")

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
        self.app_controller.reset()

        self.t = 0

        return self.get_state()

    def get_observation(self):
        return self.get_state()
