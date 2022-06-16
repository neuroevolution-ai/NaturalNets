import numpy as np
import names as n
import time

from typing import Dict, List
from widget import Widget_old
from dropdown import Dropdown
from app import App, ElementInfo


# dict mapping page-names to widget-infos

TEST_WIDGETS = {
  n.CALC: {
    n.CALC_OPERAND_ONE_DROPDOWN: {
      "state_len": 6,
      "type": Dropdown,
      "args": {
        "name": n.CALC_OPERAND_ONE_DROPDOWN,
        "items": [
          n.CALC_OPERAND_ONE_0,
          n.CALC_OPERAND_ONE_1,
          n.CALC_OPERAND_ONE_2,
          n.CALC_OPERAND_ONE_3,
          n.CALC_OPERAND_ONE_4,
        ]
      },
      "constraints": {
        n.CALC_OPERAND_ONE_4: ["constraint.mockup"] 
      }
    },
    n.CALC_OPERAND_TWO_DROPDOWN: {
      "state_len": 6,
      "type": Dropdown,
      "args": {
        "name": n.CALC_OPERAND_TWO_DROPDOWN,
        "items": [
          n.CALC_OPERAND_TWO_0,
          n.CALC_OPERAND_TWO_1,
          n.CALC_OPERAND_TWO_2,
          n.CALC_OPERAND_TWO_3,
          n.CALC_OPERAND_TWO_4,
        ]
      },
    }
  },
}

# Idea: one big dict mapping all pages to the widgets they use
# App: 1. constructs state array with len = total len of all widgets with len m
#      2. contains 
#          2.1 state 
#          2.2 constraint dict mapping state_index to constraint-state_index dict[state_index,state_index]
#          2.3 state name to state index dict
#          2.4 state_index to widget,name,page,state_sector dict (to find widget affected by input)
#          2.5 dict mapping widget names to pages (to execute page.step according to input_vector)
#          2.6 dict mapping widget names to widgets (to pass to page constructor in correct order)
#      3. constructs all widgets:
#          3.1 passes state_section for widget to widget constructor
#          3.2 gets state_name_to_state_index from widgets in {0,1,...,n}
#          3.3 fills dict mapping state_name to app.state index 
#          3.4 fills dict mapping each index to a constraint-index
#      4. constructs all pages passing the relevant widgets
#          4.1 fills dict mapping widget_name to page s.t. pages can be called when state changes
#              happen in relevant widgets
#   -> pages offer functionality depending on the relevant widget state

class TestApp:
  def __init__(self):
    # TODO: +1 only because of mockup item!
    self._state_len = 0 + 1
    self._state_in_use_index = 0
    for page in TEST_WIDGETS.values():
      for widget in page.values():
        self._state_len += widget["state_len"]
    print("total state len: ", self._state_len)
    self._state = np.zeros(self._state_len, dtype=int)

    mockup_element = {"element_name": "constraint.mockup",
                    "element_constraint_names": [],
                    "element_constraint_indexes": [],
                    "widget": None, 
                    "widget_name": None, 
                    "state_sector": (0, 0),
                    "page_name": n.SETTINGS}

    #self._state = np.zeros(self._state_len)
    #self._state_name_to_state_index:dict[str,int] = {}
    #self._state_index_to_constraint_index = {}
    #self._widget_name_to_page_name = {}


    self._state_index_to_element_info = {}
    self._widget_name_to_widget = {}

    #TODO mockup
    self._state_index_to_element_info[0] = mockup_element
    self._state_in_use_index = 1 #usually from widget_dict["state_len"]
    self._state[0] = 1

    self.add_widgets(TEST_WIDGETS)
    for index, element_info in self._state_index_to_element_info.items():
      print(index, ": ", element_info)

    # add element_constraint_indexes to all element-infos after initializing all widgets
    #  (all constraint-elements will be in state-vector then)
    self._element_name_to_state_index = {element_info["element_name"]: index for index, element_info in self._state_index_to_element_info.items()}
    for element_info in self._state_index_to_element_info.values():
      for constraint_name in element_info["element_constraint_names"]:
        element_info["element_constraint_indexes"].append(self._element_name_to_state_index[constraint_name])

    self._last_step_widget:Widget_old = None
    print(self._element_name_to_state_index)
    print("========= end init ===============")

    #page_widgets = {}
    #last_end_index = len(self._state)
    #for (k,v) in TEST_WIDGETS.items():
    #  start_index = last_end_index
    #  end_index = last_end_index + v["state_len"]
    #  state_section = self._state[start_index:end_index]
    #  page_widgets[k] = v["type"](state_section, **v["args"])

    #  nti = page_widgets[k].get_name_to_index()
    #  for i, (name, index) in enumerate(nti.items()):
    #    self._state_name_to_state_index[name] = i + index

    #  last_end_index = end_index
    #page_widgets = {k: v["type"](self._state[i:i+v["state_len"]], **v["args"]) for i, (k,v) in enumerate(TEST_WIDGETS.items())}

    """
    print("initial app widgets: ", page_widgets)
    page = Page(page_widgets)

    #self._add_elements_to_state({"padding.1": 0, "padding.2": 1})


    self.page = Page(TEST_WIDGETS)
    np.append(self._state,self.page.get_state())
    np.append(self._state, [1,0])
    print("initial state: ", self._state)
    """

  # build all widgets for all pages from dict and fill widget_info vector
  def add_widgets(self, widgets_dict) -> None:
    last_end_index = self._state_in_use_index

    for page_name, page_dict in widgets_dict.items():
      for (widget_name, widget_dict) in page_dict.items():
        widget_start_index = last_end_index
        widget_end_index = last_end_index + widget_dict["state_len"]
        state_sector = self._state[widget_start_index:widget_end_index]

        widget:Widget_old = widget_dict["type"](state_sector, **widget_dict["args"])

        # add widget to widget-name to widget map
        self._widget_name_to_widget[widget_name] = widget

        widget_enti = widget.get_element_name_to_index()
        for element_name, index in widget_enti.items():
          #add element state-index to element-info map
          element_info = {"element_name": None,
                          "element_constraint_names": [],
                          "element_constraint_indexes": [],
                          "widget": widget, 
                          "widget_name": widget_name, 
                          "state_sector": (widget_start_index, widget_end_index),
                          "page_name": page_name}

          curr_index = widget_start_index + index

          # add constraint- and element-name to element info
          element_info["element_name"] = element_name
          #TODO: build widget dict accordingly, s.t. it has constraints
          if "constraints" in widget_dict and element_name in widget_dict["constraints"]:
            element_info["element_constraint_names"].extend(widget_dict["constraints"][element_name])

          self._state_index_to_element_info[curr_index] = element_info

        last_end_index = widget_end_index
        self._state_in_use_index = last_end_index



  def step(self, action:np.ndarray):
    xor = np.logical_xor(self._state, action)
    if np.sum(xor) != 1:
      self._last_step_widget.exec_on_invalid_action()
      raise ValueError("Action differs in more than one element from last state.")
    
    index = 0
    for i in range(self._state_len):
      if xor[i] == 1:
        index = i
        break


    elem_info = self._state_index_to_element_info[i]
    for constraint_index in elem_info["element_constraint_indexes"]:
      if self._state[constraint_index] != 1:
        # at least one constraint not satisfied => invalid action
        self._last_step_widget.exec_on_invalid_action()
        return self._state


    #page = elem_info["page"] #TODO: save pages in dict
    #page = self.page
    start, end = elem_info["state_sector"]
    #TODO: normally the widget would be called with only the state-sector as input
    #      after the app checks the constraints
    #     - then page would be called to act (the page looks up the relevant state changes in its change)
    input = action[start:end] # cut portion relevant for the widget out of action
    widget = elem_info["widget"]
    print("foo")
    print("widget state: ", widget.get_state())
    widget.step(input)
    self._last_step_widget = widget


    print("action: ", input)
    #self.page.step(n.CALC_OPERAND_ONE_DROPDOWN, action[:6])
    #print("page state: ", self.page.get_state())

    # execute widget-dependent actions (e.g. closing dropdown on the next step, or 
    # settint a Button value to 0 (as it only "is clicked" for one time step))
    #if self._last_step_widget != None:
    #  self._last_step_widget.exec_on_next_step()

class Page:
  def __init__(self, widget_1):
    #self._widgets:dict[str,Widget] = {k: v["type"](**v["args"]) for (k,v) in widgets.items()}
    self._widgets = [widget_1]

  def step(self, input:np.ndarray, constraint_state:np.ndarray=None):
    self._widgets[0].step(input, constraint_state)
    pass

  def act(self, widget_name):
    #TODO: some functionality on state, e.g. for calculator: calculating
    # only if widget would trigger action
    pass

  def get_state(self):
    print([widget.get_state() for widget in self._widgets.values()])
    return np.concatenate([widget.get_state() for widget in self._widgets.values()])
    #return np.array([element for widget in self._widgets.values() for element in widget.get_state()], dtype=int)
  
  def get_state_h(self) -> Dict[str, int]:
    d = {}
    for widget in self._widgets.values():
      d.update(widget.get_state_h())
    print(d)
    return d



def find_element_index(name:str, state_index_to_element_info:Dict[int, ElementInfo]):
  for index, elem_info in state_index_to_element_info.items():
    if elem_info.name == name:
      return index

if __name__=="__main__":
  app = App()
  print("app initial state:      ", app._state)

  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERAND_ONE_DROPDOWN, app._state_index_to_element_info)
  input[i] = 1 # open first dropdown
  app.step(input)
  print("app state after step 1: ", app._state)

  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERAND_ONE_4, app._state_index_to_element_info)
  input[i] = 1 # set first dropdown to "4"
  app.step(input)
  print("app state after step 2: ", app._state)

  # open second dropdown
  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERAND_TWO_DROPDOWN, app._state_index_to_element_info)
  input[i] = 1
  app.step(input)
  print("app state after step 3: ", app._state)

  # set second dropdown to "2"
  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERAND_TWO_2, app._state_index_to_element_info)
  input[i] = 1
  app.step(input)
  print("app state after step 4: ", app._state)

  # print calculator result
  app._page.step()

  # open operator dropdown
  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERATOR_DROPDOWN, app._state_index_to_element_info)
  input[i] = 1
  app.step(input)
  print("app state after step 5: ", app._state)


  # set operator to *
  input = np.copy(app._state)
  i = find_element_index(n.CALC_OPERATOR_MULT, app._state_index_to_element_info)
  input[i] = 1
  app.step(input)
  print("app state after step 6: ", app._state)

  # print calculator result
  app._page.step()








