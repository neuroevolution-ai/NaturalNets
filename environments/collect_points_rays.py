import math

import attr
import cv2
import numpy as np

from environments.df_maze import Maze
from environments.i_environment import IEnvironment, registered_environment_classes


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class CollectPointsCfg:
    type: str
    maze_columns: int
    maze_rows: int
    maze_cell_size: int
    agent_radius: int
    point_radius: int
    agent_movement_range: float
    number_of_sensors: int
    reward_per_collected_positive_point: float
    reward_per_collected_negative_point: float
    number_time_steps: int


class Ray:
    def __init__(self, direction: np.ndarray, distance: float, maze_cell_size: int):
        self.direction = direction
        self.distance = distance

        if np.isclose(self.direction[0], 0):
            self.direction[0] = 0.0
            self.delta_dist_x = np.inf
        else:
            self.delta_dist_x = np.sqrt(1 + (self.direction[1] / self.direction[0]) * (self.direction[1] / self.direction[0]))

        if np.isclose(self.direction[1], 0):
            self.direction[1] = 0.0
            self.delta_dist_y = np.inf
        else:
            self.delta_dist_y = np.sqrt(1 + (self.direction[0] / self.direction[1]) * (self.direction[0] / self.direction[1]))

        self.delta_dist_x *= maze_cell_size
        self.delta_dist_y *= maze_cell_size

        # TODO check if this actually works. Also not sure why the outer if-s are necessary
        # if self.direction[1] == 0:
        #     self.delta_dist_x = 0
        # else:
        #     self.delta_dist_x = 1 if self.direction[0] == 0 else np.abs(1 / self.direction[0])
        #
        # if self.direction[0] == 0:
        #     self.delta_dist_y = 0
        # else:
        #     self.delta_dist_y = 1 if self.direction[1] == 0 else np.abs(1 / self.direction[1])

        # Since the maze is built so that the uppermost left corner is 0,0 and it increase from there, the step in
        # y-direction is actually mirrored compared to the description of the DDA algorithm
        self.step_x, step_y = 1, -1

        if self.direction[0] < 0:
            self.step_x = -1

        if self.direction[1] < 0:
            self.step_y = +1


class CollectPointsRays(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):
        self.config = CollectPointsCfg(**configuration)

        self.screen_width = self.config.maze_cell_size * self.config.maze_columns
        self.screen_height = self.config.maze_cell_size * self.config.maze_rows

        self.rs = np.random.RandomState(env_seed)

        # Agent coordinates
        self.agent_position_x, self.agent_position_y = self.place_randomly_in_maze(self.config.agent_radius)

        # Point coordinates for positive point
        self.point_x, self.point_y = self.place_randomly_in_maze(self.config.point_radius)

        # Point coordinates for negative point
        self.negative_point_x, self.negative_point_y = self.place_randomly_in_maze(self.config.point_radius)

        # Create Maze
        self.maze = Maze(self.config.maze_columns, self.config.maze_rows, self.rs)

        self.number_of_sensors = self.config.number_of_sensors

        if self.number_of_sensors > 0:
            self.rays = self.initialize_rays()

        # if self.number_of_sensors == 4:
        #     self.sensor_top = 0.0
        #     self.sensor_bottom = 0.0
        #     self.sensor_left = 0.0
        #     self.sensor_right = 0.0

        self.t = 0

    def get_number_inputs(self):
        return len(self.get_observation())

    def get_number_outputs(self):
        return 2

    def reset(self):
        return self.get_observation()

    def initialize_rays(self):
        def normalize(point):
            return point / np.linalg.norm(point)

        def rotate(point, angle_in_degrees):
            angle = np.radians(angle_in_degrees)
            c, s = np.cos(angle), np.sin(angle)

            rotated_point = np.array([[c, -s], [s, c]]).dot(point)

            return normalize(rotated_point)

        angle_per_ray = 360.0 / self.number_of_sensors

        first_ray = np.array([1, 0])
        rays = [Ray(first_ray, distance=0.0, maze_cell_size=self.config.maze_cell_size)]

        for i in range(1, self.number_of_sensors):
            rays.append(
                Ray(rotate(first_ray, angle_per_ray * i), distance=0.0, maze_cell_size=self.config.maze_cell_size)
            )

        return rays

    def step(self, action: np.ndarray):
        # Movement range for agent
        mr = self.config.agent_movement_range

        # Move agent
        self.agent_position_x += int(np.clip(math.floor(action[0] * mr), -mr, mr))
        self.agent_position_y += int(np.clip(math.floor(action[1] * mr), -mr, mr))

        # Check agent collisions with outer walls
        self.agent_position_y = max(self.agent_position_y, self.config.agent_radius)  # Upper border
        self.agent_position_y = min(self.agent_position_y, self.screen_height - self.config.agent_radius)  # Lower bord.
        self.agent_position_x = min(self.agent_position_x, self.screen_width - self.config.agent_radius)  # Right border
        self.agent_position_x = max(self.agent_position_x, self.config.agent_radius)  # Left border

        # Get cell indices of agents current position
        cell_x = math.floor(self.agent_position_x / self.config.maze_cell_size)
        cell_y = math.floor(self.agent_position_y / self.config.maze_cell_size)

        # Get current cell
        cell = self.maze.cell_at(cell_x, cell_y)

        # Get coordinates of current cell
        x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

        # Check agent collisions with maze walls
        if cell.walls['N']:
            self.agent_position_y = max(self.agent_position_y, y_top + self.config.agent_radius)
        if cell.walls['S']:
            self.agent_position_y = min(self.agent_position_y, y_bottom - self.config.agent_radius)
        if cell.walls['E']:
            self.agent_position_x = min(self.agent_position_x, x_right - self.config.agent_radius)
        if cell.walls['W']:
            self.agent_position_x = max(self.agent_position_x, x_left + self.config.agent_radius)

        # Check agent collision with top-left edge (prevents sneaking through the edge)
        if (self.agent_position_x - x_left < self.config.agent_radius
                and self.agent_position_y - y_top < self.config.agent_radius):
            self.agent_position_x = x_left + self.config.agent_radius
            self.agent_position_y = y_top + self.config.agent_radius

        # Check agent collision with top-right edge (prevents sneaking through the edge)
        if (x_right - self.agent_position_x < self.config.agent_radius
                and self.agent_position_y - y_top < self.config.agent_radius):
            self.agent_position_x = x_right - self.config.agent_radius
            self.agent_position_y = y_top + self.config.agent_radius

        # Check agent collision with bottom-right edge (prevents sneaking through the edge)
        if (x_right - self.agent_position_x < self.config.agent_radius
                and y_bottom - self.agent_position_y < self.config.agent_radius):
            self.agent_position_x = x_right - self.config.agent_radius
            self.agent_position_y = y_bottom - self.config.agent_radius

        # Check agent collision with bottom-left edge (prevents sneaking through the edge)
        if (self.agent_position_x - x_left < self.config.agent_radius
                and y_bottom - self.agent_position_y < self.config.agent_radius):
            self.agent_position_x = x_left + self.config.agent_radius
            self.agent_position_y = y_bottom - self.config.agent_radius

        # Get sensor signals

        if self.number_of_sensors > 0:
            self.calculate_ray_distances(cell_x=cell_x, cell_y=cell_y)

        if self.number_of_sensors == 4:
            self.sensor_top = self.get_sensor_distance('top', cell_x, cell_y)
            self.sensor_bottom = self.get_sensor_distance('bottom', cell_x, cell_y)
            self.sensor_left = self.get_sensor_distance('left', cell_x, cell_y)
            self.sensor_right = self.get_sensor_distance('right', cell_x, cell_y)

        rew = 0.0

        # Collect positive point in reach
        distance = math.sqrt((self.point_x - self.agent_position_x) ** 2 + (self.point_y - self.agent_position_y) ** 2)
        if distance <= self.config.point_radius + self.config.agent_radius:
            self.point_x, self.point_y = self.place_randomly_in_maze(self.config.point_radius)
            rew = self.config.reward_per_collected_positive_point

        # Collect negative point in reach
        distance = math.sqrt(
            (self.negative_point_x - self.agent_position_x) ** 2 + (self.negative_point_y - self.agent_position_y) ** 2)
        if distance <= self.config.point_radius + self.config.agent_radius:
            self.negative_point_x, self.negative_point_y = self.place_randomly_in_maze(self.config.point_radius)
            rew = self.config.reward_per_collected_negative_point

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        ob = self.get_observation()
        info = dict()

        if self.number_of_sensors > 0:
            for i in range(len(self.rays)):
                info["sensor_{}".format(i)] = self.rays[i].distance

        # if self.number_of_sensors == 4:
        #     info['sensor_top'] = self.sensor_top
        #     info['sensor_bottom'] = self.sensor_bottom
        #     info['sensor_right'] = self.sensor_right
        #     info['sensor_left'] = self.sensor_left

        return ob, rew, done, info

    def calculate_ray_distances(self, cell_x: int, cell_y: int):
        x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

        for current_ray in self.rays:
            current_cell_x, current_cell_y = cell_x, cell_y

            # Do DDA per ray
            if current_ray.direction[0] < 0:
                # x-dir is negative
                current_ray.step_x = -1
                # TODO continue here, calculate correct first delta to the x cell
                # Divide by maze cell size to normalize the cell to unit length TODO check if this works
                ray_length_x = (self.agent_position_x - x_left) / self.config.maze_cell_size
                ray_length_x *= current_ray.delta_dist_x
                wall_to_check_x = 'W'
            else:
                # x-dir is positive
                current_ray.step_x = 1
                ray_length_x = 1 - ((self.agent_position_x - x_left) / self.config.maze_cell_size)
                ray_length_x *= current_ray.delta_dist_x
                wall_to_check_x = 'E'
            if current_ray.direction[1] < 0:
                # y-dir is negative
                current_ray.step_y = +1
                ray_length_y = 1 - ((self.agent_position_y - y_top) / self.config.maze_cell_size)
                ray_length_y *= current_ray.delta_dist_y
                wall_to_check_y = 'S'
            else:
                # y-dir is positive
                current_ray.step_y = -1
                ray_length_y = (self.agent_position_y - y_top) / self.config.maze_cell_size
                ray_length_y *= current_ray.delta_dist_y
                wall_to_check_y = 'N'

            # If delta_dist_x or delta_dist_y is inf, then the ray_length should be inf as well. Normally this would be
            # done automatically in the if-else structure above but when for some reason ray_length_x or _y will get
            # 0.0 in the first assignment, then it will become NaN when it is multiplied with delta_dist_x or _y in the
            # second assignment. Therefore set it to inf explicitly here
            if np.isinf(current_ray.delta_dist_x):
                ray_length_x = np.inf

            if np.isinf(current_ray.delta_dist_y):
                ray_length_y = np.inf

            hit = False
            side = None

            cell = self.maze.cell_at(current_cell_x, current_cell_y)

            if ray_length_x < ray_length_y:
                if cell.walls[wall_to_check_x]:
                    hit = True
                    side = 0
            else:
                if cell.walls[wall_to_check_y]:
                    hit = True
                    side = 1

            while not hit:
                if ray_length_x < ray_length_y:
                    ray_length_x += current_ray.delta_dist_x
                    current_cell_x += current_ray.step_x
                    side = 0
                    wall_to_check = wall_to_check_x
                else:
                    ray_length_y += current_ray.delta_dist_y
                    current_cell_y += current_ray.step_y
                    side = 1
                    wall_to_check = wall_to_check_y

                # if self.is_valid_maze_cell(current_cell_x, current_cell_y):
                cell = self.maze.cell_at(current_cell_x, current_cell_y)
                # else:
                #     break

                if cell.walls[wall_to_check]:
                    hit = True

            if side == 0:
                current_ray.distance = ray_length_x - self.config.agent_radius
            elif side == 1:
                current_ray.distance = ray_length_y - self.config.agent_radius
            else:
                raise RuntimeError("Variable 'side' that indicates if ray hit in x or y direction is not set properly")

    def get_sensor_distance(self, direction: str, cell_x: int, cell_y: int) -> float:
        # Get current cell
        cell = self.maze.cell_at(cell_x, cell_y)

        # Get coordinates of current cell
        x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

        if direction == 'top':
            sensor_distance = self.agent_position_y - y_top - self.config.agent_radius
            wall_to_check = 'N'
            i_step = 0
            j_step = -1
        elif direction == 'bottom':
            sensor_distance = y_bottom - self.agent_position_y - self.config.agent_radius
            wall_to_check = 'S'
            i_step = 0
            j_step = 1
        elif direction == 'left':
            sensor_distance = self.agent_position_x - x_left - self.config.agent_radius
            wall_to_check = 'W'
            i_step = -1
            j_step = 0
        elif direction == 'right':
            sensor_distance = x_right - self.agent_position_x - self.config.agent_radius
            wall_to_check = 'E'
            i_step = 1
            j_step = 0
        else:
            raise RuntimeError("Invalid sensor direction: " + str(direction))

        i = 0
        j = 0

        while True:
            if self.is_valid_maze_cell(cell_x + i, cell_y + j):
                cell = self.maze.cell_at(cell_x + i, cell_y + j)
            else:
                break

            if cell.walls[wall_to_check]:
                break
            else:
                sensor_distance += self.config.maze_cell_size
                i += i_step
                j += j_step

        return sensor_distance

    def is_valid_maze_cell(self, cell_x: int, cell_y: int) -> bool:
        if 0 <= cell_x < self.config.maze_columns and 0 <= cell_y < self.config.maze_rows:
            return True
        else:
            return False

    def render(self):

        red = (0, 0, 255)
        green = (0, 255, 0)
        black = (0, 0, 0)
        blue = (255, 0, 0)
        orange = (0, 88, 255)

        # Initialize image with white background
        image = 255 * np.ones(shape=[self.screen_width, self.screen_height, 3], dtype=np.uint8)

        # Draw agent
        image = cv2.circle(image, (self.agent_position_x, self.agent_position_y), self.config.agent_radius, green, -1)

        # Draw positive point
        image = cv2.circle(image, (self.point_x, self.point_y), self.config.point_radius, blue, -1)

        # Draw negative point
        image = cv2.circle(image, (self.negative_point_x, self.negative_point_y), self.config.point_radius, red, -1)

        # Draw maze
        for cell_x in range(self.config.maze_columns):
            for cell_y in range(self.config.maze_rows):

                x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

                cell = self.maze.maze_map[cell_x][cell_y]

                # Draw walls
                if cell.walls['N']:
                    image = cv2.line(image, (x_left, y_top), (x_right, y_top), black, 2)
                if cell.walls['S']:
                    image = cv2.line(image, (x_left, y_bottom), (x_right, y_bottom), black, 2)
                if cell.walls['E']:
                    image = cv2.line(image, (x_right, y_top), (x_right, y_bottom), black, 2)
                if cell.walls['W']:
                    image = cv2.line(image, (x_left, y_top), (x_left, y_bottom), black, 2)

        # Draw outer border
        image = cv2.rectangle(image, (0, 0), (self.screen_width - 1, self.screen_height - 1), black, 3)

        # Render rays
        if self.number_of_sensors > 0:
            for current_ray in self.rays:

                # TODO figure out clever way to get the offset with the agent_radius right
                pos_x, pos_y = self.agent_position_x, self.agent_position_y

                # Offset the player position by the agent radius so that they ray starts at the edge of the player
                # circle, when rendering
                pos_x = round(pos_x + current_ray.direction[0] * self.config.agent_radius)
                pos_y = round(pos_y - current_ray.direction[1] * self.config.agent_radius)

                pt1 = (pos_x, pos_y)
                pt2 = (round(pos_x + current_ray.direction[0] * current_ray.distance),
                       round(pos_y - current_ray.direction[1] * current_ray.distance))

                image = cv2.line(image, pt1=pt1, pt2=pt2, color=orange, thickness=1)

        # # Render sensors lines
        # if self.number_of_sensors == 4:
        #     # Render sensor line top
        #     image = cv2.line(image,
        #                      (self.agent_position_x, self.agent_position_y - self.config.agent_radius),
        #                      (
        #                      self.agent_position_x, self.agent_position_y - self.config.agent_radius - self.sensor_top),
        #                      orange,
        #                      1)
        #
        #     # Render sensor line bottom
        #     image = cv2.line(image,
        #                      (self.agent_position_x, self.agent_position_y + self.config.agent_radius),
        #                      (self.agent_position_x,
        #                       self.agent_position_y + self.config.agent_radius + self.sensor_bottom),
        #                      orange,
        #                      1)
        #
        #     # Render sensor line left
        #     image = cv2.line(image,
        #                      (self.agent_position_x - self.config.agent_radius, self.agent_position_y),
        #                      (self.agent_position_x - self.config.agent_radius - self.sensor_left,
        #                       self.agent_position_y),
        #                      orange,
        #                      1)
        #
        #     # Render sensor line left
        #     image = cv2.line(image,
        #                      (self.agent_position_x + self.config.agent_radius, self.agent_position_y),
        #                      (self.agent_position_x + self.config.agent_radius + self.sensor_right,
        #                       self.agent_position_y),
        #                      orange,
        #                      1)

        cv2.imshow("ProcGen Agent", cv2.resize(image, (self.screen_width, self.screen_height)))
        cv2.waitKey(1)

    def get_coordinates_maze_cell(self, cell_x, cell_y):

        x_left = self.config.maze_cell_size * cell_x
        x_right = self.config.maze_cell_size * (cell_x + 1)
        y_top = self.config.maze_cell_size * cell_y
        y_bottom = self.config.maze_cell_size * (cell_y + 1)

        return x_left, x_right, y_top, y_bottom

    def get_observation(self):

        ob_list = list()
        ob_list.append(self.agent_position_x / self.screen_width)
        ob_list.append(self.agent_position_y / self.screen_height)

        if self.number_of_sensors > 0:
            for i in range(len(self.rays)):
                # TODO old version divided by screen_height and screen_width, is this necessary? Also what would be to
                #      do if non orthogonal rays are used
                ob_list.append(self.rays[i].distance)

        # if self.number_of_sensors == 4:
        #     ob_list.append(self.sensor_top / self.screen_height)
        #     ob_list.append(self.sensor_bottom / self.screen_height)
        #     ob_list.append(self.sensor_left / self.screen_width)
        #     ob_list.append(self.sensor_right / self.screen_width)

        ob_list.append(self.point_x / self.screen_width)
        ob_list.append(self.point_y / self.screen_height)
        ob_list.append(self.negative_point_x / self.screen_width)
        ob_list.append(self.negative_point_y / self.screen_height)

        return np.asarray(ob_list)

    def place_randomly_in_maze(self, radius):

        x = self.rs.randint(radius, self.config.maze_cell_size - radius) + self.rs.randint(
            self.config.maze_columns) * self.config.maze_cell_size

        y = self.rs.randint(radius, self.config.maze_cell_size - radius) + self.rs.randint(
            self.config.maze_rows) * self.config.maze_cell_size

        return x, y


# TODO: Do this registration via class decorator
registered_environment_classes['CollectPointsRays'] = CollectPointsRays
