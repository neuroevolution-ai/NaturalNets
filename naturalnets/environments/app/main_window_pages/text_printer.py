from typing import List
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.constants import IMAGES_PATH, MAIN_PAGE_AREA_BB
from naturalnets.environments.app.enums import Font, FontStyle
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.utils import put_text
from naturalnets.environments.app.widgets.button import Button

class TextPrinter(Page):

    STATE_LEN = 2
    IMG_PATH = IMAGES_PATH + "text_printer.png"

    BUTTON_BB = BoundingBox(125, 406, 303, 22)
    TEXT_AREA_BB = BoundingBox(135, 48, 286, 183) # area adjusted to only show properties (bb does not match the grafical bb)

    def __init__(self):
        super().__init__(self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        self._font_styles:list[FontStyle] = []
        self._font:Font = Font.DEJAVU_SANS
        self._font_size = 12
        self._color = Color.BLACK
        self._n_words = 50

        self.button = Button(self.BUTTON_BB, lambda: self.print_text())

    def set_font_style(self, style:FontStyle, enabled:bool) -> None:
        if enabled:
            self._font_styles.append(style)
        else:
            self._font_styles.remove(style)

    def set_font(self, font:Font) -> None:
        self._font = font
        
    def set_font_size(self, size:int) -> None:
        self._font_size = size

    def set_color(self, color:Color) -> None:
        self._color = color

    def set_n_words(self, n:int) -> None:
        self._n_words = n

    def print_text(self):
        self.get_state()[0] = 1

    def handle_click(self, click_position: np.ndarray = None):
        if self.button.is_clicked_by(click_position):
            self.button.handle_click()

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.get_state()[0] == 1: # text is shown
            x, y, _, height = self.TEXT_AREA_BB.get_as_tuple()
            bottomLeftCorner = lambda i: (x, y + height - i)
            props = ["Number of words: {}".format(self._n_words), "Font: {}".format(self._font.value),
                     "Font Size: {}".format(self._font_size), "Color: {}".format(self._color),
                     "Font Stylez: {}".format([font_style.value for font_style in self._font_styles])]
            SPACE = 20
            for i in range(len(props)):
                put_text(img, props[i], bottomLeftCorner(i*SPACE), 0.4)

        return img

