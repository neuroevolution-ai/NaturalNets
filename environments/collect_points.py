import numpy as np
import cv2
import math
from gym.envs.registration import register

#register(
#    id="CollectPoints-v0",
#    entry_point="environments.envs:CollectPointsEnv",
#    max_episode_steps=1000  # Arbitrarily chosen, can be overwritten in the CollectPointsEnv class
#)


class CollectPointsEnv:

    def __init__(self, env_seed):

        self.number_of_time_steps = 300

        self.screen_width = 800
        self.screen_height = 800

        # Radius of agent
        self.agent_radius = 10
        self.point_radius = 8

        # Agent coordinates
        self.agent_position_x = 400
        self.agent_position_y = 400

        self.sensor_range = 100

        self.seed = env_seed

        self.point_x = self.generate_random_number(self.screen_width)
        self.point_y = self.generate_random_number(self.screen_height)

        self.t = 0

    def get_number_inputs(self):
        return len(self.get_observation())

    def get_number_outputs(self):
        return 2

    def reset(self):
        return self.get_observation()

    def step(self, action: np.ndarray):

        self.agent_position_x += int(action[0] * 10)
        self.agent_position_y += int(action[1] * 10)

        self.agent_position_x = min(self.agent_position_x, self.screen_height - self.agent_radius)
        self.agent_position_x = max(self.agent_position_x, self.agent_radius)
        self.agent_position_y = min(self.agent_position_y, self.screen_width - self.agent_radius)
        self.agent_position_y = max(self.agent_position_y, self.agent_radius)

        # Collect point in reach

        distance = math.sqrt((self.point_x - self.agent_position_x) ** 2 + (self.point_y - self.agent_position_y) ** 2)
        if distance > self.point_radius + self.agent_radius:
            rew = -distance / self.screen_width
        else:
            self.point_x = self.generate_random_number(self.screen_width)
            self.point_y = self.generate_random_number(self.screen_height)
            rew = 500.0

        self.t += 1

        if self.t < self.number_of_time_steps:
            done = False
        else:
            done = True

        ob = self.get_observation()
        info = []

        return ob, rew, done, info

    def render(self):

        color_red = (0, 0, 255)
        color_blue = (0, 255, 0)

        image = 255 * np.ones(shape=[self.screen_width, self.screen_height, 3], dtype=np.uint8)

        # Draw agent
        image = cv2.circle(image, (self.agent_position_x, self.agent_position_y), self.agent_radius, color_red, -1)

        # Draw point
        image = cv2.circle(image, (self.point_x, self.point_y), self.point_radius, color_blue, -1)

        cv2.imshow("ProcGen Agent", cv2.resize(image, (self.screen_width, self.screen_height)))
        cv2.waitKey(1)

    # https://stackoverflow.com/questions/39714326/random-number-generation-using-python
    # Generates a random number between 0.0 and 1.0
    def generate_random_number(self, range: int):

        m = 2 ** 32
        a = 1664525
        c = 1013904223

        self.seed = (a * self.seed + c) % m
        return int((self.seed / (2 ** 32 - 1)) * range)

    def get_observation(self):

        ob_list = list()
        ob_list.append(self.agent_position_x / self.screen_width)
        ob_list.append(self.agent_position_y / self.screen_height)
        ob_list.append(self.point_x / self.screen_width)
        ob_list.append(self.point_y / self.screen_height)

        return np.asarray(ob_list)
