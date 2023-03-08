from typing import List

import numpy as np

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.enums import Font, FontStyle
from naturalnets.environments.app_components.interfaces import Clickable
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.utils import put_text, get_image_path
from naturalnets.environments.app_components.widgets.button import Button


class TextPrinter(Page, RewardElement):
    """The text-printer page in the main-window.

       State description:
            state[0]: Denotes if the text is currently shown.
    """

    STATE_LEN = 1
    MAX_CLICKABLE_ELEMENTS = 1

    IMG_PATH = get_image_path(IMAGES_PATH, "text_printer.png")

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    # For rendering purposes (position of the rendered text), the text-area bounding box
    # does not match the graphical 'box' of the text area, but was adjusted to fit the
    # text generated by display_text()
    TEXT_AREA_BB = BoundingBox(135, 48, 286, 183)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self._font_styles: List[FontStyle] = []
        self._font = None
        self._font_size = None
        self._color = None
        self._n_words = None

        self.button = Button(self.BUTTON_BB, self.print_text)
        self.display_dict = None

    @property
    def reward_template(self):
        return {
            "word_count": [50, 100, 200, 400],
            "word_count_setting": [50, 100, 200, 400],
            "font_size": [12, 14, 16, 18, 20],
            "font_size_setting": [12, 14, 16, 18, 20],
            "font": [Font.DEJAVU_SANS, Font.LIBERATION_MONO, Font.NIMBUS_ROMAN, Font.UBUNTU],
            "font_setting": [Font.DEJAVU_SANS, Font.LIBERATION_MONO, Font.NIMBUS_ROMAN, Font.UBUNTU],
            "font_color": [Color.RED, Color.GREEN, Color.BLUE, Color.BLACK],
            "font_color_setting": [Color.RED, Color.GREEN, Color.BLUE, Color.BLACK],
            "font_style": {
                FontStyle.BOLD: [False, True],
                FontStyle.ITALIC: [False, True],
                FontStyle.UNDERLINE: [False, True]
            },
            "font_style_setting": {
                FontStyle.BOLD: [False, True],
                FontStyle.ITALIC: [False, True],
                FontStyle.UNDERLINE: [False, True]
            }
        }

    def reset(self):
        self.display_dict = None
        self._font_styles: List[FontStyle] = []
        self._font: Font = Font.DEJAVU_SANS
        self._font_size = 12
        self._color: Color = Color.BLACK
        self._n_words = 50

        # Initially the output is not printed, thus set the state to 0
        self.get_state()[0] = 0

    def set_font_style(self, style: FontStyle, enabled: int) -> None:
        if enabled:
            self._font_styles.append(style)
        else:
            try:
                self._font_styles.remove(style)
            except ValueError:
                # Do nothing, the font is already removed
                pass

        self.register_selected_reward(
            ["font_style_setting", style, bool(enabled)])

    def set_font(self, font: Font) -> None:
        self._font = font

        self.register_selected_reward(["font_setting", font])

    def set_font_size(self, size: int) -> None:
        self._font_size = size

        self.register_selected_reward(["font_size_setting", size])

    def set_color(self, color: Color) -> None:
        self._color = color

        self.register_selected_reward(["font_color_setting", color])

    def set_n_words(self, n: int) -> None:
        self._n_words = n

        self.register_selected_reward(["word_count_setting", n])

    def print_text(self):
        self.display_dict = self.update_display_dict()
        self.get_state()[0] = 1

        for font_style in FontStyle:
            if font_style in self._font_styles:
                self.register_selected_reward(["font_style", font_style, True])
            else:
                self.register_selected_reward(
                    ["font_style", font_style, False])

        self.register_selected_reward(["font", self._font])
        self.register_selected_reward(["font_size", self._font_size])
        self.register_selected_reward(["font_color", self._color])
        self.register_selected_reward(["word_count", self._n_words])

    def handle_click(self, click_position: np.ndarray = None):
        if self.button.is_clicked_by(click_position):
            self.button.handle_click(click_position)

    def update_display_dict(self):
        return {
            "n_words": self._n_words,
            "font": self._font.value,
            "font_size": self._font_size,
            "font_styles": [font_style.value for font_style in self._font_styles],
            "color": self._color
        }

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.get_state()[0] == 1:  # text is shown
            self.display_text(img)

        return img

    def display_text(self, img):
        """Renders the text-settings onto the text area."""
        x, y, _, height = self.TEXT_AREA_BB.get_as_tuple()
        props = [f"Number of words: {self.display_dict['n_words']}",
                 f"Font: {self.display_dict['font']}",
                 f"Font Size: {self.display_dict['font_size']}",
                 f"Color: {self.display_dict['color']}",
                 f"Font Styles: {self.display_dict['font_styles']}"]
        space = 20
        for i, prop in enumerate(props):
            bottom_left_corner = (x, y + height - i * space)
            put_text(img, prop, bottom_left_corner, font_scale=0.4)

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        clickable_elements.append(self.button)

        return clickable_elements
