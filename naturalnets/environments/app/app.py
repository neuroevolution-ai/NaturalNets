from cmath import inf
from re import I
import numpy as np
import random
import attr
import cv2
import math
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes

from typing import Dict, List, Tuple
from widget import Widget
from exception import InvalidInputError
from calculator import Calculator
from widgets_dict import WIDGETS_DICT


#TODO
@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    type: str
    number_time_steps: int
    screen_width: int
    screen_height: int
    number_buttons_horizontal: int
    number_buttons_vertical: int
    buttons_size_horizontal: int
    buttons_size_vertical: int

@attr.s(slots=True, auto_attribs=True, kw_only=True)
class ElementInfo:
    name:str
    constraint_names:List[str] = []
    constraint_indexes:List[int] = []
    widget:Widget
    widget_name:str
    state_sector:Tuple[int,int]
    page_name:str

class App(IEnvironment):

    def __init__(self, env_seed: int, configuration: dict):
        self._state_len:int = 0 
        self._last_allocated_state_index:int = 0
        self._state_index_to_element_info:Dict[int,ElementInfo] = {}
        self._widget_name_to_widget:Dict[str,Widget] = {}

        # init state array
        for page in WIDGETS_DICT.values():
            for widget in page.values():
                self._state_len += widget["state_len"]

        print("App init: total state len: ", self._state_len)
        self._state = np.zeros(self._state_len, dtype=int)

        # add all widgets
        self.add_widgets(WIDGETS_DICT)
        self._initial_state = np.copy(self._state)

        # add element_constraint_indexes to all element-infos after initializing all widgets
        #  (all constraint-elements will be in state-vector then)
        self._element_name_to_state_index = {element_info["element_name"]: index for index, element_info in self._state_index_to_element_info.items()}
        for element_info in self._state_index_to_element_info.values():
            for constraint_name in element_info["element_constraint_names"]:
                element_info["element_constraint_indexes"].append(self._element_name_to_state_index[constraint_name])

        print("App init: done.")


    ########################################################
    ## Methods implemented because DummyApp has them:     ##
    ########################################################

    def get_number_inputs(self):
        return self._state_len

    def get_number_outputs(self):
        return self._state_len

    def reset(self):
        self._state[:] = self._initial_state

    def is_action_valid(self, action: np.ndarray):
        # exactly one element of the input vector has to differ from the state (last output)
        #TODO: only holds for intaractable parts of state, e.g. result of calculater
        #      can differ in multiple elements of the vector!
        xor = np.logical_xor(self.state, action)
        return xor.sum() == 1

    def get_interacted_widget(self, action: np.ndarray) -> Widget:
        #TODO: should return the widget the action interacts with
        raise NotImplementedError

    def get_constraint_state_for_widget(self, widget: Widget) -> Dict[str,int]:
        #TODO: should return a dict containing a map from constraint names (from names.py)
        #      of the widget to the values in the current state vector
        raise NotImplementedError

    def interrupt_action(self) -> None:
        # TODO: choose an interrupt-action (e.g. in Calculator settings when selecting green
        # radio button)
        # - probably need index of action + dict where index maps to interrupt-action
        raise NotImplementedError

    def step(self, action: np.ndarray):

        if not self.is_action_valid():
            return self.state

        if self.last_interacted_widget != None:
            self.last_interacted_widget.exec_on_next_step()
        # TODO: find where action and state differ -> extract which widget is concerned 
        #         -> only call that widgets handle_input() -> return state
        self.last_interacted_widget = self.get_interacted_widget(action)
        contraint_state = self.get_constraint_state_for_widget(self.last_interacted_widget)

        # TODO: Widget.is_interactable() probably not necessary, just save non-interactable
        #  part of self.state and check if it was tampered with in self.is_action_valid
        # if self.last_interacted_widget.is_interactable():
        if not self.interrupt_action():
            try:
                # update state
                self.last_interacted_widget.handle_input(action, contraint_state)
            except InvalidInputError:
                return self.state

        return self.state





        #### old stuff from here down ####

        action = np.tanh(action)

        random_number1 = action[2] * np.random.normal()
        random_number2 = action[3] * np.random.normal()
        self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
        self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        self.action = action

        #self.click_position_x = random.randint(1, self.config.screen_width)
        #self.click_position_y = random.randint(1, self.config.screen_height)

        #button = random.randrange(self.number_buttons)
        #self.click_position_x = self.gui_elements_rectangles[button, 0] + 1
        #self.click_position_y = self.gui_elements_rectangles[button, 1] + 1

        rew = 0.0

        # Find chosen button based on mouse click position
        minimal_distance = inf
        button = 0
        for i in range(self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            distance = self.rect_distance(self.click_position_x, self.click_position_y, rect_x, rect_y, width, height)

            if distance < minimal_distance:
                minimal_distance = distance
                button = i

            if distance < 0.0001:
                break

        if button == 0:
            if self.gui_elements_states[0] == 0:
                rew += 1.0
                self.gui_elements_states[0] = 1
        else:
            if self.gui_elements_states[button] == 0 and self.gui_elements_states[button-1] == 1:
                rew += 1.0
                self.gui_elements_states[button] = 1

        self.t += 1

        if self.t < self.config.number_time_steps:
            done = False
        else:
            done = True

        ob = self.get_observation()
        info = dict()

        return ob, rew, done, info

    def get_observation(self):
        return self.gui_elements_states

    def render(self):

        red = (0, 0, 255)
        green = (0, 255, 0)
        black = (0, 0, 0)
        grey = (100, 100, 100)
        blue = (255, 0, 0)
        orange = (0, 88, 255)

        image = cv2.imread('naturalnets/environments/dummy_app.png')

        # Buttons
        for i in range(self.number_buttons):

            rect_x = self.gui_elements_rectangles[i, 0]
            rect_y = self.gui_elements_rectangles[i, 1]
            width = self.gui_elements_rectangles[i, 2]
            height = self.gui_elements_rectangles[i, 3]

            point1 = (rect_x, rect_y)
            point2 = (rect_x + width, rect_y + height)

            if self.gui_elements_states[i] == 0:
                color = red
            else:
                color = green

            image = cv2.rectangle(image, point1, point2, color, 1)

        # Click areas
        n = 0
        for i in range(self.config.number_buttons_vertical):
            for j in range(self.config.number_buttons_horizontal):

                x = int(self.grid_size_horizontal * i)
                y = int(self.grid_size_vertical * j)
                width = int(self.grid_size_horizontal)
                height = int(self.grid_size_vertical)

                button = self.buttons[n]
                n += 1

                #image = cv2.putText(
                #    img=image,
                #    text=str(button+1),
                #    org=(x, int(y + height*0.5)),
                #    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                #    fontScale=0.5,
                #    color=black,
                #    thickness=1
                #)

                image = cv2.rectangle(image, (x, y), (x + width, y + height), grey, 1)

        # Action distribution as ellipse
        action_position_x = int(0.5 * (self.action[0] + 1.0) * self.config.screen_width)
        action_position_y = int(0.5 * (self.action[1] + 1.0) * self.config.screen_height)
        action_distribution_x = abs(int(0.5 * self.action[2] * self.config.screen_width))
        action_distribution_y = abs(int(0.5 * self.action[3] * self.config.screen_height))
        image = cv2.ellipse(image, (action_position_x, action_position_y),(action_distribution_x, action_distribution_y), 0, 0, 360, orange, 1)

        # Click position
        image = cv2.circle(image, (self.click_position_x, self.click_position_y), 3, blue, -1)

        cv2.imshow("Dummy App", image)
        cv2.waitKey(1)

    def is_point_in_rect(self, point_x, point_y, rect_x, rect_y, width, height):

        return rect_x <= point_x <= (rect_x + width) and rect_y <= point_y <= (rect_y + height)

    # https://stackoverflow.com/questions/5254838/calculating-distance-between-a-point-and-a-rectangular-box-nearest-point
    def rect_distance(self, point_x, point_y, rect_x, rect_y, width, height):
        dx = max(rect_x - point_x, 0, point_x - rect_x - width)
        dy = max(rect_y - point_y, 0, point_y - rect_y - height)

        return math.sqrt(dx*dx + dy*dy)


# TODO: Do this registration via class decorator
registered_environment_classes['DummyApp'] = DummyApp
