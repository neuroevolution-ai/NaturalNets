import numpy as np
import attr
from environments.df_maze import Maze
import cv2
import math
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


class CollectPoints(IEnvironment):

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

        if self.number_of_sensors == 4:
            self.sensor_top = 0.0
            self.sensor_bottom = 0.0
            self.sensor_left = 0.0
            self.sensor_right = 0.0

        self.t = 0

    def get_number_inputs(self):
        return len(self.get_observation())

    def get_number_outputs(self):
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

        # Get cell indizes of agents current position
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

        # Get sensor signals
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
        info = dict()

        if self.number_of_sensors == 4:
            info['sensor_top'] = self.sensor_top
            info['sensor_bottom'] = self.sensor_bottom
            info['sensor_right'] = self.sensor_right
            info['sensor_left'] = self.sensor_left

        return ob, rew, done, info

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
            if self.is_valid_maze_cell(cell_x+i, cell_y+j):
                cell = self.maze.cell_at(cell_x+i, cell_y+j)
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
        image = cv2.rectangle(image, (0, 0), (self.screen_width-1, self.screen_height-1), black, 3)

        # Render sensors lines
        if self.number_of_sensors == 4:

            # Render sensor line top
            image = cv2.line(image,
                             (self.agent_position_x, self.agent_position_y - self.config.agent_radius),
                             (self.agent_position_x, self.agent_position_y - self.config.agent_radius - self.sensor_top),
                             orange,
                             1)

            # Render sensor line bottom
            image = cv2.line(image,
                             (self.agent_position_x, self.agent_position_y + self.config.agent_radius),
                             (self.agent_position_x, self.agent_position_y + self.config.agent_radius + self.sensor_bottom),
                             orange,
                             1)

            # Render sensor line left
            image = cv2.line(image,
                             (self.agent_position_x - self.config.agent_radius, self.agent_position_y),
                             (self.agent_position_x - self.config.agent_radius - self.sensor_left, self.agent_position_y),
                             orange,
                             1)

            # Render sensor line left
            image = cv2.line(image,
                             (self.agent_position_x + self.config.agent_radius, self.agent_position_y),
                             (self.agent_position_x + self.config.agent_radius + self.sensor_right, self.agent_position_y),
                             orange,
                             1)

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

        if self.number_of_sensors == 4:
            ob_list.append(self.sensor_top / self.screen_height)
            ob_list.append(self.sensor_bottom / self.screen_height)
            ob_list.append(self.sensor_left / self.screen_width)
            ob_list.append(self.sensor_right / self.screen_width)

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
registered_environment_classes['CollectPoints'] = CollectPoints
