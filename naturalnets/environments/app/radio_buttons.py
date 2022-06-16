import numpy as np

from widget import Widget_old

class RadioButtons(Widget_old):
  def __init__(self, state_sector: np.ndarray, name: str):
      super().__init__(state_sector, name)

