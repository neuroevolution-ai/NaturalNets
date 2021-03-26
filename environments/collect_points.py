import numpy as np
import attr
from environments.df_maze import Maze
import cv2
import math


@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class CollectPointsCfg:
    type: str
    maze_columns: int
    maze_rows: int
    maze_cell_size: int
    agent_radius: int
    point_radius: int
    agent_movement_range: float
    reward_per_collected_positive_point: float
    reward_per_collected_negative_point: float
    number_time_steps: int


class CollectPoints:

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

        self.t = 0

    def get_number_inputs(self):
        return len(self.get_observation())

    @staticmethod
    def get_number_outputs():
        return 2

    def reset(self):
        return self.get_observation()

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

        # Check agent collisions with maze walls
        cell_x = math.floor(self.agent_position_x / self.config.maze_cell_size)
        cell_y = math.floor(self.agent_position_y / self.config.maze_cell_size)

        x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

        cell = self.maze.cell_at(cell_x, cell_y)

        if cell.walls['N']:
            self.agent_position_y = max(self.agent_position_y, y_top + self.config.agent_radius)
        if cell.walls['S']:
            self.agent_position_y = min(self.agent_position_y, y_bottom - self.config.agent_radius)
        if cell.walls['E']:
            self.agent_position_x = min(self.agent_position_x, x_right - self.config.agent_radius)
        if cell.walls['W']:
            self.agent_position_x = max(self.agent_position_x, x_left + self.config.agent_radius)

        # Check agent collision with top-left edge (prevents sneaking through the edge)
        if self.agent_position_x - x_left < self.config.agent_radius \
                and self.agent_position_y - y_top < self.config.agent_radius:
            self.agent_position_x = x_left + self.config.agent_radius
            self.agent_position_y = y_top + self.config.agent_radius

        # Check agent collision with top-right edge (prevents sneaking through the edge)
        if x_right - self.agent_position_x < self.config.agent_radius \
                and self.agent_position_y - y_top < self.config.agent_radius:
            self.agent_position_x = x_right - self.config.agent_radius
            self.agent_position_y = y_top + self.config.agent_radius

        # Check agent collision with bottom-right edge (prevents sneaking through the edge)
        if x_right - self.agent_position_x < self.config.agent_radius \
                and y_bottom - self.agent_position_y < self.config.agent_radius:
            self.agent_position_x = x_right - self.config.agent_radius
            self.agent_position_y = y_bottom - self.config.agent_radius

        # Check agent collision with bottom-left edge (prevents sneaking through the edge)
        if self.agent_position_x - x_left < self.config.agent_radius \
                and y_bottom - self.agent_position_y < self.config.agent_radius:
            self.agent_position_x = x_left + self.config.agent_radius
            self.agent_position_y = y_bottom - self.config.agent_radius

        rew = 0.0

        # Collect positive point in reach
        distance = math.sqrt((self.point_x - self.agent_position_x) ** 2 + (self.point_y - self.agent_position_y) ** 2)
        if distance <= self.config.point_radius + self.config.agent_radius:
            self.point_x, self.point_y = self.place_randomly_in_maze(self.config.point_radius)
            rew = self.config.reward_per_collected_positive_point

        # Collect negative point in reach
        distance = math.sqrt((self.negative_point_x - self.agent_position_x) ** 2 + (self.negative_point_y - self.agent_position_y) ** 2)
        if distance <= self.config.point_radius + self.config.agent_radius:
            self.negative_point_x, self.negative_point_y = self.place_randomly_in_maze(self.config.point_radius)
            rew = self.config.reward_per_collected_negative_point

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        ob = self.get_observation()
        info = []

        return ob, rew, done, info

    def render(self):

        red = (0, 0, 255)
        green = (0, 255, 0)
        black = (0, 0, 0)
        blue = (255, 0, 0)

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
        image = cv2.rectangle(image, (0, 0), (self.screen_width-1, self.screen_height-1), black, 3)

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
