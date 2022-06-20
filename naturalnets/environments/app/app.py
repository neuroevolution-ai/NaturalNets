from cmath import inf
from importlib.util import spec_from_file_location
from re import I
import numpy as np
#import random
import attr
import cv2
#import cv2
#import math
import time
from naturalnets.environments.app.check_box import CheckBox
#from naturalnets.environments.app.element_bounding_box import ElementBB
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.elements import Elements
from naturalnets.environments.app.main_window import MainWindow
from naturalnets.environments.app.settings_window import SettingsWindow
from naturalnets.environments.i_environment import IEnvironment, registered_environment_classes

from typing import Dict, List, Tuple
from naturalnets.environments.app.widget import Widget_old
from naturalnets.environments.app.exception import InvalidInputError
from naturalnets.environments.app.calculator import Calculator
from naturalnets.environments.app.widgets_dict import MAIN_WINDOW_PAGES, SETTINGS_WINDOW_PAGES, SETTINGS_WINDOW_PAGES_NEW


#TODO
@attr.s(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class AppCfg:
    number_time_steps: int
    screen_width: int
    screen_height: int
    interactive: bool

@attr.s(slots=True, auto_attribs=True, kw_only=True)
class ElementInfo:
    name:str
    constraint_names:List[str] = []
    constraint_indexes:List[int] = []
    widget:Widget_old
    widget_name:str
    state_sector:Tuple[int,int]
    page_name:str

class App(IEnvironment):
    def __init__(self, configuration: dict, env_seed: int=None):

        self.config = AppCfg(**configuration)
        self.action = None

        self._state_len:int = MainWindow.STATE_LEN + SettingsWindow._STATE_LEN
        for page_dict in SETTINGS_WINDOW_PAGES.values():
            self._state_len += page_dict["state_len"]
            for widget_dict in page_dict["widgets"]:
                self._state_len += widget_dict["state_len"]

        self._state = np.zeros(self._state_len, dtype=int)
        self._last_allocated_state_index:int = 0

        #settings_window_pages = {}
        #for page_elem, page_dict in SETTINGS_WINDOW_PAGES.items():
        #    page_widgets = []
        #    for widget_dict in page_dict["widgets"]:
        #        state_sector = self.get_next_state_sector(widget_dict["state_len"])
        #        widget = widget_dict["type"](state_sector, **widget_dict["args"])
        #        page_widgets.append(widget)
        #    settings_window_pages[page_elem] = {"navigator": page_dict["navigator"], "widgets": page_widgets}

        #settings_window_pages = {}
        settings_pages = []
        for page in SETTINGS_WINDOW_PAGES_NEW:
            page_state_sector = self.get_next_state_sector(page.get_state_len())
            page_widgets = []
            for widget in page.get_widget_dicts():
                state_sector = self.get_next_state_sector(widget_dict["state_len"])
                widget = widget_dict["type"](state_sector, **widget_dict["args"])
                page_widgets.append(widget)
            settings_pages.append(page(page_state_sector, page_widgets))
            


        #self._state_len += CheckBox.STATE_LEN

        settings_state_sector = self.get_next_state_sector(SettingsWindow._STATE_LEN)
        self.settings = SettingsWindow(settings_state_sector, settings_window_pages)

        main_window_state_sector = self.get_next_state_sector(MainWindow.STATE_LEN)
        self.main_window = MainWindow(main_window_state_sector, self.settings)

        assert self._last_allocated_state_index == len(self._state)


        print("App init: done.")

    def get_next_state_sector(self, state_len):
        sector_end = self._last_allocated_state_index + state_len
        sector = self._state[self._last_allocated_state_index:sector_end]
        self._last_allocated_state_index = sector_end
        return sector

    def step(self, action: np.ndarray):
        if self.config.interactive:
            self.click_position_x = action[0]
            self.click_position_y = action[1]
        else:
            action = np.tanh(action)

            random_number1 = action[2] * np.random.normal()
            random_number2 = action[3] * np.random.normal()
            self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
            self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        click_coordinates = np.array([self.click_position_x, self.click_position_y])
        #print(click_coordinates)
        self.main_window.handle_click(click_coordinates)

        print("current state:", self._state)

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("x:", x, ", y:", y)
            self.action = np.array([x,y,10,10])

    def render(self):
        #TODO: get img depending on current state
        #IMG_PATH:str = 'naturalnets/environments/app/img/'
        #current_img_name:str = self.main_window.get_current_img_name()
        #image = cv2.imread(IMG_PATH + current_img_name)
        #print(current_img_name)

        image = self.main_window.render()

        if self.config.interactive:
            cv2.imshow("App", image)
            cv2.setMouseCallback("App", self.click_event)
            while True:
                ESC_KEY = 27
                input_key = cv2.waitKey(10)
                if input_key == ESC_KEY:
                    # return None as exit "action"
                    cv2.destroyAllWindows()
                    return None
                if self.action is not None:
                    # click sets self.action -> return action
                    action = np.copy(self.action)
                    self.action = None
                    return action
        else:
            cv2.imshow("App", image)
            cv2.waitKey(1)
        


#class App():

    #def __init__(self, env_seed: int, configuration: dict):
    def __init__old_(self, configuration: dict, env_seed: int=None):

        self.config = AppCfg(**configuration)
        self.action = None

        self._state_len:int = 0 
        self._last_allocated_state_index:int = 0
        self._state_index_to_element_info:Dict[int,ElementInfo] = {}
        self._widget_name_to_widget:Dict[str,Widget_old] = {}
        self._last_step_widget:Widget_old = None

        self._page = None #TODO: only for testing

        # init state array
        t_0 = time.time()
        for page_dict in PAGES_DICT.values():
            self._state_len += page_dict["state_len"]
            for widget in page_dict["widgets"].values():
                self._state_len += widget["state_len"]
        t_1 = time.time()
        print("App init: got state len from widgets dict. Time ellapsed:", t_1-t_0)
        print("App init: total state len: ", self._state_len)

        self._state:np.ndarray = np.zeros(self._state_len, dtype=int)

        # add all widgets
        t_2 = time.time()
        self.add_widgets(PAGES_DICT)
        t_3 = time.time()
        print("App init: initialized all widgets. Time ellapsed:", t_3-t_2)
        self._initial_state:np.ndarray = np.copy(self._state)

        # add element_constraint_indexes to all element-infos after initializing all widgets
        #  (all constraint-elements will be in state-vector then)
        self._element_name_to_state_index = {element_info.name: index for index, element_info in self._state_index_to_element_info.items()}
        for element_info in self._state_index_to_element_info.values():
            for constraint_name in element_info.constraint_names:
                element_info.constraint_indexes.append(self._element_name_to_state_index[constraint_name])

        print("App init: done.")

    # build all widgets for all pages from dict and fill widget_info vector
    def add_widgets(self, widgets_dict) -> None:
        for page_name, page_dict in widgets_dict.items():
            page_widgets = {}

            for (widget_name, widget_dict) in page_dict["widgets"].items():
                widget_start_index = self._last_allocated_state_index
                widget_end_index = widget_start_index + widget_dict["state_len"]
                state_sector = self._state[widget_start_index:widget_end_index]

                widget:Widget_old = widget_dict["type"](state_sector, **widget_dict["args"])
                page_widgets[widget_name] = widget

                # add widget to widget_name_to_widget map
                self._widget_name_to_widget[widget_name] = widget

                # add all ElementInfos for the widget elements to state_index_to_element_info
                widget_enti = widget.get_element_name_to_index()
                for element_name, index in widget_enti.items():
                    curr_index:int = widget_start_index + index

                    element_info = ElementInfo(name=element_name, widget=widget, 
                                               widget_name=widget_name, page_name=page_name,
                                               state_sector=(widget_start_index,widget_end_index))

                    # add constrait names from widget_dict, constraint_indexes can only be set when all
                    # state-elements/widgets/pages have been initialized
                    if "constraints" in widget_dict and element_name in widget_dict["constraints"]:
                        element_info.constraint_names.extend(widget_dict["constraints"][element_name])

                    self._state_index_to_element_info[curr_index] = element_info

                self._last_allocated_state_index = widget_end_index

            # add pages
            sector_start_index = self._last_allocated_state_index
            sector_end_index = sector_start_index + page_dict["state_len"]
            state_sector = self._state[sector_start_index:sector_end_index]
            page = page_dict["type"](state_sector, page_widgets)
            self._page = page

            self._last_allocated_state_index = widget_end_index

    def step_old(self, action: np.ndarray):
        action = np.tanh(action)

        random_number1 = action[2] * np.random.normal()
        random_number2 = action[3] * np.random.normal()
        self.click_position_x = int(0.5 * (action[0] + 1.0 + random_number1) * self.config.screen_width)
        self.click_position_y = int(0.5 * (action[1] + 1.0 + random_number2) * self.config.screen_height)

        t_0 = time.time()
        try:
            index = self._get_action_index(action)
        except InvalidInputError:
            self._on_invalid_input_error()
            return self._state

        elem_info = self._state_index_to_element_info[index]
        try:
            self._check_constraints(elem_info)
        except InvalidInputError:
            self._on_invalid_input_error()
            return self._state


        #page = elem_info["page"] #TODO: save pages in dict
        start, end = elem_info.state_sector
        input = action[start:end] # cut portion relevant for the widget out of action
        widget = elem_info.widget
        try:
            widget.step(input)
            #page.step() #TODO
        except InvalidInputError:
            self._on_invalid_input_error()
            return self._state

        self._last_step_widget = widget
        t_1 = time.time()
        #print("App step took", t_1-t_0)

    # This should probably be optimized by using an appropriate data-structure, e.g. quadtrees
    def _get_clicked_widget(self, action:np.ndarray):
        """Returns the widget affected by the given action, None if the action did not 
        affect an interactable part of the application.

        Args:
            action (np.ndarray): array containing the xy-coordinates of the click-action

        Returns:
            _type_: the interacted widget, None if no interactable position was clicked.
        """

        #TODO: action contains x,y coords of click
        #TODO: initialize and update self.current_frame_widgets: UPDATE: schould probably be elements, not widgets?
        #TODO: self.current_fram_widgets need to be ordered s.t. widgets "overlaying" other
        #      widgets will be processed first (e.g. opened dropdown "overlaying" button beneath it)
        for widget in self.current_frame_widgets:
            #TODO: initialize and update bounding_box of widgets (may depend on widget state)
            bounding_box = widget.get_bounding_box()
            x = action[0]
            y = action[1]
            if self._is_point_inside_bounding_box(bounding_box, x, y):
                return widget

        return None # no widget clicked = click on some non-interactable part of application

    def _is_point_inside_bounding_box(self, bounding_box:BoundingBox, x, y) -> bool:
        """Returns true if the given x and y are inside the bounding box (including its borders).
        """
        x1 = bounding_box.x
        x2 = x1 + bounding_box.width
        y1 = bounding_box.y
        y2 = y2 + bounding_box.height
        return x1 <= x <= x2 and y1 <= y <= y2



    def _get_action_index(self, action:np.ndarray) -> None:
        xor = np.logical_xor(self._state, action)
        if np.sum(xor) != 1:
            raise InvalidInputError("Action differs in more than one element from last state.")
        
        for i in range(self._state_len):
            if xor[i] == 1:
                return i

    # execute widget-dependent actions (e.g. closing an opened dropdown)
    # on invalid action (interpreted as click)
    def _on_invalid_input_error(self) -> None:
        if self._last_step_widget != None:
            self._last_step_widget.exec_on_invalid_action()
            self._last_step_widget = None

    def _check_constraints(self, elem_info:ElementInfo) -> None:
        for constraint_index in elem_info.constraint_indexes:
            if self._state[constraint_index] != 1:
                raise InvalidInputError("At least one constraint not satisfied.")

    def interrupt_action(self) -> None:
        # TODO: choose an interrupt-action (e.g. in Calculator settings when selecting green
        # radio button)
        # - probably need index of action + dict where index maps to interrupt-action
        # - interrupt actions could just be called executed by the widget itself,
        #   e.g. inheriting from RadioButtons and changing the functionality of
        #    _mutate_state()
        raise NotImplementedError

    ########################################################
    ## Methods implemented because DummyApp has them:     ##
    ########################################################

    def get_number_inputs(self) -> int:
        return self._state_len

    def get_number_outputs(self) -> int:
        return self._state_len

    def reset(self) -> None:
        self._state[:] = self._initial_state

    def get_observation(self):
        return self._state


        #raise NotImplementedError

# TODO: Do this registration via class decorator
#registered_environment_classes['App'] = App
