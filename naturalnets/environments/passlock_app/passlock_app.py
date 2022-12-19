import logging
import time
from naturalnets.environments.i_environment import IEnvironment, register_environment_class
from naturalnets.environments.passlock_app.app_controller import PasslockAppController


@register_environment_class
class PasslockApp(IEnvironment):

    screen_width: int = 1100
    screen_height: int = 850

    def __init__(self, **kwargs):

        if "env_seed" in kwargs:
            logging.warning("'env_seed' is not used in the GUIApp environment")
        t0 = time.time()

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