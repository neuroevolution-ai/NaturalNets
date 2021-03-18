import numpy as np
from environments.df_maze import Maze
import cv2
import math


class CollectPointsEnv:

    def __init__(self, env_seed):

        self.number_of_time_steps = 1000

        # Maze dimensions (ncols, nrows)
        self.nx, self.ny = 10, 10
        self.maze_cell_size = 80

        self.screen_width = self.maze_cell_size * self.nx
        self.screen_height = self.maze_cell_size * self.ny

        # Radius of agent
        self.agent_radius = 12
        self.point_radius = 8

        self.rs = np.random.RandomState(env_seed)

        # Agent coordinates
        self.agent_position_x = self.rs.randint(self.screen_width)
        self.agent_position_y = self.rs.randint(self.screen_height)

        self.point_x = self.rs.randint(self.screen_width)
        self.point_y = self.rs.randint(self.screen_height)

        # Create Maze
        self.maze = Maze(self.nx, self.ny, self.rs)

        self.t = 0

    def get_number_inputs(self):
        return len(self.get_observation())

    def get_number_outputs(self):
        return 2

    def reset(self):
        return self.get_observation()

    def step(self, action: np.ndarray):

        # Move agent
        self.agent_position_x += math.floor(action[0] * 10)
        self.agent_position_y += math.floor(action[1] * 10)

        # Check agent collisions with outer walls
        self.agent_position_y = max(self.agent_position_y, self.agent_radius)  # Upper border
        self.agent_position_y = min(self.agent_position_y, self.screen_height - self.agent_radius)  # Lower border
        self.agent_position_x = min(self.agent_position_x, self.screen_width - self.agent_radius)  # Right border
        self.agent_position_x = max(self.agent_position_x, self.agent_radius)  # Left border

        # Check agent collisions with maze walls
        cell_x = math.floor(self.agent_position_x / self.maze_cell_size)
        cell_y = math.floor(self.agent_position_y / self.maze_cell_size)

        x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

        cell = self.maze.cell_at(cell_x, cell_y)

        if cell.walls['N']:
            self.agent_position_y = max(self.agent_position_y, y_top + self.agent_radius)
        if cell.walls['S']:
            self.agent_position_y = min(self.agent_position_y, y_bottom - self.agent_radius)
        if cell.walls['E']:
            self.agent_position_x = min(self.agent_position_x, x_right - self.agent_radius)
        if cell.walls['W']:
            self.agent_position_x = max(self.agent_position_x, x_left + self.agent_radius)

        # Collect point in reach
        distance = math.sqrt((self.point_x - self.agent_position_x) ** 2 + (self.point_y - self.agent_position_y) ** 2)
        if distance > self.point_radius + self.agent_radius:
            rew = -distance / self.screen_width
        else:
            self.point_x = self.rs.randint(self.screen_width)
            self.point_y = self.rs.randint(self.screen_height)
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
        color_black = (0, 0, 0)

        image = 255 * np.ones(shape=[self.screen_width, self.screen_height, 3], dtype=np.uint8)

        # Draw agent
        image = cv2.circle(image, (self.agent_position_x, self.agent_position_y), self.agent_radius, color_red, -1)

        # Draw point
        image = cv2.circle(image, (self.point_x, self.point_y), self.point_radius, color_blue, -1)

        # Render maze
        for cell_x in range(self.nx):
            for cell_y in range(self.ny):

                x_left, x_right, y_top, y_bottom = self.get_coordinates_maze_cell(cell_x, cell_y)

                cell = self.maze.maze_map[cell_x][cell_y]

                # Render walls
                if cell.walls['N']:
                    image = cv2.line(image, (x_left, y_top), (x_right, y_top), color_black, 2)
                if cell.walls['S']:
                    image = cv2.line(image, (x_left, y_bottom), (x_right, y_bottom), color_black, 2)
                if cell.walls['E']:
                    image = cv2.line(image, (x_right, y_top), (x_right, y_bottom), color_black, 2)
                if cell.walls['W']:
                    image = cv2.line(image, (x_left, y_top), (x_left, y_bottom), color_black, 2)

        # Draw outer border
        image = cv2.rectangle(image, (0, 0), (self.screen_width-1, self.screen_height-1), color_black, 3)

        cv2.imshow("ProcGen Agent", cv2.resize(image, (self.screen_width, self.screen_height)))
        cv2.waitKey(1)

    def get_coordinates_maze_cell(self, cell_x, cell_y):

        x_left = self.maze_cell_size * cell_x
        x_right = self.maze_cell_size * (cell_x + 1)
        y_top = self.maze_cell_size * cell_y
        y_bottom = self.maze_cell_size * (cell_y + 1)

        return x_left, x_right, y_top, y_bottom

    def get_observation(self):

        ob_list = list()
        ob_list.append(self.agent_position_x / self.screen_width)
        ob_list.append(self.agent_position_y / self.screen_height)
        ob_list.append(self.point_x / self.screen_width)
        ob_list.append(self.point_y / self.screen_height)

        return np.asarray(ob_list)
