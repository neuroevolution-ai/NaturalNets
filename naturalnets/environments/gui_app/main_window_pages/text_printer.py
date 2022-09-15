import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.enums import Font, FontStyle
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.utils import put_text
from naturalnets.environments.gui_app.widgets.button import Button


class TextPrinter(Page):
    """The text-printer page in the main-window.

       State description:
            state[0]: Denotes if the text is currently shown.
    """

    STATE_LEN = 1
    IMG_PATH = os.path.join(IMAGES_PATH, "text_printer.png")

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    # For rendering purposes (position of the rendered text), the text-area bounding box
    # does not match the graphical 'box' of the text area, but was adjusted to fit the
    # text generated by display_text()
    TEXT_AREA_BB = BoundingBox(135, 48, 286, 183)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self._font_styles: List[FontStyle] = []
        self._font: Font = Font.DEJAVU_SANS
        self._font_size = 12
        self._color = Color.BLACK
        self._n_words = 50

        self.button = Button(self.BUTTON_BB, self.print_text)
        self.display_dict = None

        self.reward_dict = {}

    def reset_reward_dict(self):
        self.reward_dict = {
            "word_count": {
                50: 0,
                100: 0,
                200: 0,
                400: 0
            },
            "word_count_setting": {
                50: 0,
                100: 0,
                200: 0,
                400: 0
            },
            "font_size": {
                12: 0,
                14: 0,
                16: 0,
                18: 0,
                20: 0
            },
            "font_size_setting": {
                12: 0,
                14: 0,
                16: 0,
                18: 0,
                20: 0
            },
            "font": {
                Font.DEJAVU_SANS: 0,
                Font.LIBERATION_MONO: 0,
                Font.NIMBUS_ROMAN: 0,
                Font.UBUNTU: 0
            },
            "font_setting": {
                Font.DEJAVU_SANS: 0,
                Font.LIBERATION_MONO: 0,
                Font.NIMBUS_ROMAN: 0,
                Font.UBUNTU: 0
            },
            "font_color": {
                Color.RED: 0,
                Color.GREEN: 0,
                Color.BLUE: 0,
                Color.BLACK: 0
            },
            "font_color_setting": {
                Color.RED: 0,
                Color.GREEN: 0,
                Color.BLUE: 0,
                Color.BLACK: 0
            },
            "font_style": {
                FontStyle.BOLD: {
                    False: 0,
                    True: 0
                },
                FontStyle.ITALIC: {
                    False: 0,
                    True: 0
                },
                FontStyle.UNDERLINE: {
                    False: 0,
                    True: 0
                }
            },
            "font_style_setting": {
                FontStyle.BOLD: {
                    False: 0,
                    True: 0
                },
                FontStyle.ITALIC: {
                    False: 0,
                    True: 0
                },
                FontStyle.UNDERLINE: {
                    False: 0,
                    True: 0
                }
            }
        }

    def set_font_style(self, style: FontStyle, enabled: int) -> None:
        if enabled:
            self._font_styles.append(style)
        else:
            self._font_styles.remove(style)

        self.reward_dict["font_style_setting"][style][bool(enabled)] = 1

    def set_font(self, font: Font) -> None:
        self._font = font

        self.reward_dict["font_setting"][font] = 1

    def set_font_size(self, size: int) -> None:
        self._font_size = size

        self.reward_dict["font_size_setting"][size] = 1

    def set_color(self, color: Color) -> None:
        self._color = color

        self.reward_dict["font_color_setting"][color] = 1

    def set_n_words(self, n: int) -> None:
        self._n_words = n

        self.reward_dict["word_count_setting"][n] = 1

    def print_text(self):
        self.display_dict = self.update_display_dict()
        self.get_state()[0] = 1

        for font_style in FontStyle:
            if font_style in self._font_styles:
                self.reward_dict["font_style"][font_style][True] = 1
            else:
                self.reward_dict["font_style"][font_style][False] = 1

        self.reward_dict["font"][self._font] = 1
        self.reward_dict["font_size"][self._font_size] = 1
        self.reward_dict["font_color"][self._color] = 1
        self.reward_dict["word_count"][self._n_words] = 1

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

    def reset(self):
        pass
