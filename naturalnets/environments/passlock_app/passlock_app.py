from ast import List
import logging
import os
import time
from typing import Dict, Optional
from attr import define, field, validators
import cv2
import jsonlines
import numpy as np
from naturalnets.enhancers.random_enhancer import RandomEnhancer
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.i_environment import IEnvironment, register_environment_class
from naturalnets.environments.passlock_app.app_controller import PasslockAppController
from naturalnets.tools.utils import rescale_values


@define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str = field(validator=validators.instance_of(str))
    number_time_steps: int = field(validator=[validators.instance_of(int), validators.gt(0)])
    include_fake_bug: bool = field(validator=validators.instance_of(bool))
    #fake_bugs: List[str] = field(default=None,
     #                            validator=[validators.optional(validators.in_([opt.value for opt in FakeBugOptions]))])

    def __attrs_post_init__(self):
        if self.include_fake_bug:
            assert self.fake_bugs is not None and len(self.fake_bugs) > 0, ("'include_fake_bug' is set to True, please "
                                                                            "provide a list of fake bugs using 'fake_"
                                                                            "bugs'.")

@register_environment_class
class PasslockApp(IEnvironment):

    screen_width: int = 1920
    screen_height: int = 1080

    def __init__(self, configuration: dict, **kwargs):

        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
        t0 = time.time()

        self.config = AppCfg(**configuration)

        self.app_controller = PasslockAppController()

        self.t = 0

        # Keep track of the last click position for rendering purposes
        self.click_position_x = 0
        self.click_position_y = 0

        # Used for the interactive mode, in which the user can click through an OpenCV rendered
        # version of the app
        self.window_name = "Passlock-App"
        self.action = None
        self.clicked = False

        self.running_reward = 0
        self.max_reward = self.app_controller.get_total_reward_len()

        t1 = time.time()

        logging.debug(f"App initialized in {t1 - t0}s.")
        logging.debug(f"Total app state length is {self.app_controller.get_total_state_len()}.")

    def get_state(self):
        return self.app_controller.get_total_state()

    def step(self, action: np.ndarray):
        # Convert from [-1, 1] continuous values to pixel coordinates in [0, screen_width/screen_height]
        #self.click_position_x = int(0.5 * (action[0] + 1.0) * self.screen_width)
        #self.click_position_y = int(0.5 * (action[1] + 1.0) * self.screen_height)
        
        #click_coordinates = np.array([self.click_position_x, self.click_position_y])
        click_coordinates = np.array([action[0], action[1]])
        #print(click_coordinates)

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

        return self.get_observation(), rew, done, {'states_info': self.app_controller.get_states_info()}

    def _render_image(self):
        img_shape = (self.screen_width, self.screen_height, 3)
        image = np.zeros(img_shape, dtype=np.uint8)
        image = self.app_controller.render(image)

        return image
 
    def render(self, enhancer_info: Optional[Dict[str, np.ndarray]] = None):
        image = self._render_image()

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
    
    def click_event(self, event, x, y, _flags, _params):
        """Sets action when cv2 mouse-callback is detected, i.e. user has clicked."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.action = np.array([x, y])
            self.clicked = True

    def interactive_mode(self, print_reward: bool = False, save_screenshots: bool = False, save_state_vector: bool = False):
        # Create the window here first, so that the callback can be registered
        # The callback simply registers the clicks of a user
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.click_event)

        # Create out directory if it does not exist yet (this directory should be added to .gitignore)
        if (save_screenshots or save_state_vector) and not os.path.exists('out'):
            os.makedirs('out')

        while True:
            current_action = None
            if self.clicked:
                current_action = self.action
                ob, rew, _, info = self.step(current_action)
                self.clicked = False

                if print_reward:
                    print(f"Reward: {rew}")

                if save_state_vector:
                    states = []
                    for state_info, state in zip(info['states_info'], ob):
                        states.append(str(state_info) + " " + str(state))

                    with jsonlines.open(os.path.join('out', 'state_vector.jsonl'), 'w') as writer:
                        writer.write_all(states)

            image = self._render_image()

            if save_screenshots:
                cv2.imwrite(os.path.join('out', 'screenshot.png'), image)

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
                    c

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

        self.click_position_x = 0
        self.click_position_y = 0

        self.action = None
        self.clicked = False

        self.running_reward = 0
        self.max_reward = self.app_controller.get_total_reward_len()

        return self.get_state()

    def get_observation(self):
        return self.get_state()