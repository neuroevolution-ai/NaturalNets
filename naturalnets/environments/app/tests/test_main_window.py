import unittest
from xml.dom.minidom import Element
import numpy as np
from naturalnets.environments.app.elements import Elements

from naturalnets.environments.app.main_window import MainWindow
from naturalnets.environments.app.settings_window import SettingsWindow

class TestMainWindow(unittest.TestCase):

  def setup(self):
    state = np.zeros(MainWindow.STATE_LEN)
    settings = SettingsWindow(np.zeros(SettingsWindow.STATE_LEN))
    main_window = MainWindow(state, settings)
    return (state, settings, main_window)

  def test_init(self):
    expected = np.array([1,0,0,0])
    state, settings, main_window = self.setup()
    np.testing.assert_array_equal(state, expected)

  def test_pages_buttons(self):
    state, settings, main_window = self.setup()
    click = np.array([Elements.CALCULATOR_BUTTON.bounding_box.x + 0,
                      Elements.CALCULATOR_BUTTON.bounding_box.y + 0])
    main_window.handle_click(click)
    expected = np.array([0,1,0,0])
    np.testing.assert_array_equal(state, expected)

    click = np.array([Elements.CAR_CONFIGURATOR_BUTTON.bounding_box.x + 0,
                      Elements.CAR_CONFIGURATOR_BUTTON.bounding_box.y + 0])
    main_window.handle_click(click)
    expected = np.array([0,0,1,0])
    np.testing.assert_array_equal(state, expected)

    click = np.array([Elements.FIGURE_PRINTER_BUTTON.bounding_box.x + 0,
                      Elements.FIGURE_PRINTER_BUTTON.bounding_box.y + 0])
    main_window.handle_click(click)
    expected = np.array([0,0,0,1])
    np.testing.assert_array_equal(state, expected)

    click = np.array([Elements.TEXT_PRINTER_BUTTON.bounding_box.x + 0,
                      Elements.TEXT_PRINTER_BUTTON.bounding_box.y + 0])
    main_window.handle_click(click)
    expected = np.array([1,0,0,0])
    np.testing.assert_array_equal(state, expected)

  # TODO: - test button click inside buttons (x+x', y+y') and lower-right edge
  #       - test clicks outside of widgets (no state change)

  def test_settings_button(self):
    state, settings, main_window = self.setup()
    click = np.array([Elements.SETTINGS_BUTTON.bounding_box.x + 0,
                      Elements.SETTINGS_BUTTON.bounding_box.y + 0])
    self.assertFalse(settings.is_opened())
    main_window.handle_click(click)
    self.assertTrue(settings.is_opened())




