import numpy as np

from widget import Widget

class RadioButtons(Widget):
  def __init__(self, state_sector: np.ndarray, name: str):
      super().__init__(state_sector, name)

