import enum
import logging
import time
from typing import Optional, Dict, List

import cv2
import numpy as np
from attrs import define, field, validators

from naturalnets.enhancers import RandomEnhancer
from naturalnets.environments.gui_app.app_controller import AppController
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.app_components.interfaces import Clickable
from naturalnets.environments.i_environment import register_environment_class, IGUIEnvironment


class FakeBugOptions(enum.Enum):
    pass


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str = field(validator=validators.instance_of(str))
    number_time_steps: int = field(
        validator=[validators.instance_of(int), validators.gt(0)])
    include_fake_bug: bool = field(validator=validators.instance_of(bool))
    fake_bugs: List[str] = field(default=None,
                                 validator=[validators.optional(validators.in_([opt.value for opt in FakeBugOptions]))])

    # If true, calculates the currently clickable elements of the GUIApp, which can then be retrieved via a method
    return_clickable_elements: bool = field(
        default=False, validator=validators.instance_of(bool))

    # If true, for each click the nearest clickable element will be calculated and this one will be clicked.
    # Thus, each click will be on a clickable element
    nearest_widget_click: bool = field(
        default=False, validator=validators.instance_of(bool))

    @nearest_widget_click.validator
    def validate_nearest_widget_click(self, attribute, value):
        if value and not self.return_clickable_elements:
            raise ValueError("GUIApp: 'nearest_widget_click' is set to True, but 'return_clickable_elements' "
                             "is set to False.\nHowever, 'return_clickable_elements' is required for "
                             "'nearest_widget_click' to work, thus try setting it to True.")

    def __attrs_post_init__(self):
        if self.include_fake_bug:
            assert self.fake_bugs is not None and len(self.fake_bugs) > 0, ("'include_fake_bug' is set to True, please "
                                                                            "provide a list of fake bugs using 'fake_"
                                                                            "bugs'.")


@register_environment_class
class GUIApp(IGUIEnvironment):

    screen_width: int = 448
    screen_height: int = 448

    def __init__(self, configuration: dict, **kwargs):
        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
        t0 = time.time()

        self.config = AppCfg(**configuration)

        self.app_controller = AppController(self.config.nearest_widget_click)

        self.t = 0

        # Keep track of the last click position for rendering purposes
        self.click_position_x = 0
        self.click_position_y = 0

        # Used for the interactive mode, in which the user can click through an OpenCV rendered
        # version of the app
        self.window_name = "App"
        self.running_reward = 0
        self.max_reward = self.app_controller.get_total_reward_len()

        t1 = time.time()

        logging.debug(f"App initialized in {t1 - t0}s.")
        logging.debug(
            f"Total app state length is {self.app_controller.get_total_state_len()}.")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):
        # Convert from [-1, 1] continuous values to pixel coordinates in [0, screen_width/screen_height]
        self.click_position_x = int(
            0.5 * (action[0] + 1.0) * self.screen_width)
        self.click_position_y = int(
            0.5 * (action[1] + 1.0) * self.screen_height)

        click_coordinates = np.array(
            [self.click_position_x, self.click_position_y])
        rew = self.app_controller.handle_click(click_coordinates)

        # For the running_reward only count the actual reward from the GUIApp, and ignore the time step calculations
        self.running_reward += rew

        # Give a reward equal to the number of time steps at the beginning to avoid negative rewards
        if self.t == 0:
            rew += self.config.number_time_steps

        # Give a negative reward of 1 for each time step
        rew -= 1

        done = False

        self.t += 1

        if self.t >= self.config.number_time_steps or self.running_reward >= self.max_reward:
            done = True

        info = {"states_info": self.app_controller.get_states_info()}

        if self.config.return_clickable_elements:
            info["clickable_elements"] = self.get_clickable_elements()

        return self.get_observation(), rew, done, info

    def render_image(self) -> np.ndarray:
        img_shape = (self.screen_width, self.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)

        return image

    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]] = None):
        image = self.render_image()

        # Draw the click position
        cv2.circle(
            image,
            (self.click_position_x, self.click_position_y),
            radius=4, color=Color.BLACK.value, thickness=-1, lineType=cv2.LINE_AA
        )

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
                    color=Color.ORANGE.value)

        cv2.imshow(self.window_name, image)
        cv2.waitKey(1)

    def get_number_inputs(self) -> int:
        return self.app_controller.get_total_state_len()

    def get_number_outputs(self) -> int:
        return 2

    def reset(self, env_seed: int = None) -> np.ndarray:
        self.app_controller.reset()

        self.t = 0

        self.click_position_x = 0
        self.click_position_y = 0

        self.running_reward = 0
        self.max_reward = self.app_controller.get_total_reward_len()

        return self.get_state()

    def get_observation(self):
        return self.get_state()

    def get_observation_dict(self) -> dict:
        raise NotImplementedError()

    def get_window_name(self) -> str:
        return self.window_name

    def get_screen_size(self) -> int:
        assert self.screen_width == self.screen_height
        return self.screen_width

    def get_screen_height(self) -> int:
        return self.screen_height

    def get_screen_width(self) -> int:
        return self.screen_width

    def get_clickable_elements(self) -> Optional[List[Clickable]]:
        if self.config.return_clickable_elements:
            return self.app_controller.get_clickable_elements()
        else:
            return None
