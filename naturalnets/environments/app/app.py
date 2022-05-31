from cmath import inf
from importlib.util import spec_from_file_location
from re import I
import numpy as np
#import random
import attr
#import cv2
#import math
import time
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
#class App():

    #def __init__(self, env_seed: int, configuration: dict):
    def __init__(self):
        self._state_len:int = 0 
        self._last_allocated_state_index:int = 0
        self._state_index_to_element_info:Dict[int,ElementInfo] = {}
        self._widget_name_to_widget:Dict[str,Widget] = {}
        self._last_step_widget:Widget = None

        self._page = None #TODO: only for testing

        # init state array
        t_0 = time.time()
        for page_dict in WIDGETS_DICT.values():
            self._state_len += page_dict["state_len"]
            for widget in page_dict["widgets"].values():
                self._state_len += widget["state_len"]
        t_1 = time.time()
        print("App init: got state len from widgets dict. Time ellapsed:", t_1-t_0)
        print("App init: total state len: ", self._state_len)

        self._state:np.ndarray = np.zeros(self._state_len, dtype=int)

        # add all widgets
        t_2 = time.time()
        self.add_widgets(WIDGETS_DICT)
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

                widget:Widget = widget_dict["type"](state_sector, **widget_dict["args"])
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

    def step(self, action: np.ndarray):
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

    def render(self):
        #TODO
        raise NotImplementedError

# TODO: Do this registration via class decorator
#registered_environment_classes['App'] = App
