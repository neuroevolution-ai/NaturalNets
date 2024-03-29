from typing import List

import numpy as np

from naturalnets.environments.app_components.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.gui_app.enums import Font, FontStyle
from naturalnets.environments.app_components.interfaces import Clickable
from naturalnets.environments.gui_app.main_window_pages.text_printer import TextPrinter
from naturalnets.environments.app_components.page import Page
from naturalnets.environments.app_components.reward_element import RewardElement
from naturalnets.environments.app_components.utils import get_image_path
from naturalnets.environments.app_components.widgets.button import Button
from naturalnets.environments.app_components.widgets.check_box import CheckBox
from naturalnets.environments.app_components.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.app_components.widgets.radio_button_group import RadioButton, RadioButtonGroup


class TextPrinterSettings(Page, RewardElement):
    """The text-printer settings page, manipulates the text-printer page."""
    STATE_LEN = 0
    CLICKABLE_ELEMENTS = 10

    IMG_PATH = get_image_path(IMAGES_PATH, "text_printer_settings.png")

    N_WORDS_BB = BoundingBox(217, 71, 173, 22)
    FONT_SIZE_BB = BoundingBox(38, 110, 87, 22)
    FONT_BB = BoundingBox(131, 110, 259, 22)

    RED_RB_BB = BoundingBox(38, 152, 46, 14)
    GREEN_RB_BB = BoundingBox(38, 178, 55, 14)
    BLUE_RB_BB = BoundingBox(217, 152, 47, 14)
    BLACK_RB_BB = BoundingBox(217, 178, 52, 14)

    BOLD_BB = BoundingBox(38, 215, 46, 14)
    ITALIC_BB = BoundingBox(38, 241, 47, 14)
    UNDERLINE_BB = BoundingBox(38, 267, 75, 14)

    def __init__(self, text_printer: TextPrinter):
        Page.__init__(self, self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.text_printer = text_printer

        # init popup
        self.popup = TextPrinterSettingsPopup(self)
        self.add_child(self.popup)

        # init font-style checkboxes
        self.bold = CheckBox(
            self.BOLD_BB,
            lambda is_checked: self.text_printer.set_font_style(
                FontStyle.BOLD, is_checked)
        )
        self.italic = CheckBox(
            self.ITALIC_BB,
            lambda is_checked: self.text_printer.set_font_style(
                FontStyle.ITALIC, is_checked)
        )
        self.underline = CheckBox(
            self.UNDERLINE_BB,
            lambda is_checked: self.text_printer.set_font_style(
                FontStyle.UNDERLINE, is_checked)
        )
        self.font_style_checkboxes = [self.bold, self.italic, self.underline]
        self.add_widgets(self.font_style_checkboxes)

        # Init dropdowns
        # Number of words dropdown
        self.n_words_50_ddi = DropdownItem(50, "50")
        self.n_words_100_ddi = DropdownItem(100, "100")
        self.n_words_200_ddi = DropdownItem(200, "200")
        self.n_words_400_ddi = DropdownItem(400, "400")
        self.n_words_ddis = [
            self.n_words_50_ddi,
            self.n_words_100_ddi,
            self.n_words_200_ddi,
            self.n_words_400_ddi
        ]
        self.n_words_dd = Dropdown(self.N_WORDS_BB, self.n_words_ddis)
        self.n_words_dd.set_selected_item(self.n_words_50_ddi)

        # Font size dropdown
        self.font_size_12 = DropdownItem(12, "12")
        self.font_size_14 = DropdownItem(14, "14")
        self.font_size_16 = DropdownItem(16, "16")
        self.font_size_18 = DropdownItem(18, "18")
        self.font_size_20 = DropdownItem(20, "20")
        self.font_size_ddis = [
            self.font_size_12,
            self.font_size_14,
            self.font_size_16,
            self.font_size_18,
            self.font_size_20
        ]
        self.font_size_dd = Dropdown(self.FONT_SIZE_BB, self.font_size_ddis)
        self.font_size_dd.set_selected_item(self.font_size_12)

        # Font dropdown: DejaVu Sans, Liberation Mono, Nimbus Roman, Ubuntu
        self.font_ds_ddi = DropdownItem(
            Font.DEJAVU_SANS, Font.DEJAVU_SANS.value)
        self.font_lm_ddi = DropdownItem(
            Font.LIBERATION_MONO, Font.LIBERATION_MONO.value)
        self.font_nr_ddi = DropdownItem(
            Font.NIMBUS_ROMAN, Font.NIMBUS_ROMAN.value)
        self.font_u_ddi = DropdownItem(Font.UBUNTU, Font.UBUNTU.value)
        self.font_ddis = [self.font_ds_ddi, self.font_lm_ddi,
                          self.font_nr_ddi, self.font_u_ddi]
        self.fonts_dd = Dropdown(self.FONT_BB, self.font_ddis)
        self.fonts_dd.set_selected_item(self.font_ds_ddi)

        # n-words dropdown needs to be first since it may occlude the
        # others when opened (important for iteration in handle_click)
        self.dropdowns: List[Dropdown] = [
            self.n_words_dd, self.font_size_dd, self.fonts_dd]
        self.dropdown_to_func = {
            self.n_words_dd: lambda: self.text_printer.set_n_words(self.n_words_dd.get_current_value()),
            self.font_size_dd: lambda: self.text_printer.set_font_size(self.font_size_dd.get_current_value()),
            self.fonts_dd: lambda: self.text_printer.set_font(
                self.fonts_dd.get_current_value())
        }

        self.dropdowns_to_str = {
            self.n_words_dd: "word_count",
            self.font_size_dd: "font_size",
            self.fonts_dd: "font"
        }

        self.add_widgets(self.dropdowns)

        self.opened_dd: Optional[Dropdown] = None

        # Init radio button group
        self.red_rb = RadioButton(self.RED_RB_BB, value=Color.RED)
        self.green_rb = RadioButton(
            self.GREEN_RB_BB, value=Color.GREEN, action=self.open_popup)
        self.blue_rb = RadioButton(self.BLUE_RB_BB, value=Color.BLUE)
        self.black_rb = RadioButton(self.BLACK_RB_BB, value=Color.BLACK)
        self.rbg = RadioButtonGroup(
            [self.black_rb, self.red_rb, self.green_rb, self.blue_rb])
        self.add_widget(self.rbg)

        self.set_reward_children([self.popup])

    @property
    def reward_template(self):
        return {
            "dropdown_opened": [
                "word_count",
                "font_size",
                "font"
            ]
        }

    def reset(self):
        self.popup.close()

        self.n_words_dd.close()
        self.n_words_dd.set_selected_item(self.n_words_50_ddi)

        self.font_size_dd.close()
        self.font_size_dd.set_selected_item(self.font_size_12)

        self.fonts_dd.close()
        self.fonts_dd.set_selected_item(self.font_ds_ddi)

        self.rbg.set_selected_button(self.black_rb)

        self.bold.set_selected(0)
        self.italic.set_selected(0)
        self.underline.set_selected(0)

    def open_popup(self):
        """Opens the text-printer settings popup, if the green radio-button is not
        selected. Should only be called when the green radio button is clicked."""
        if not self.green_rb.is_selected():
            self.popup.open()

    def set_selected_rb(self, radio_button: RadioButton) -> None:
        """Sets the selected radio button.

        Args:
            radio_button (RadioButton): The radio button to select, must be in self.rbg
        """
        self.rbg.set_selected_button(radio_button)
        self.text_printer.set_color(radio_button.get_value())

    def is_dropdown_open(self) -> bool:
        return self.opened_dd is not None

    def handle_click(self, click_position: np.ndarray = None):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        if self.opened_dd is not None:
            self.opened_dd.handle_click(click_position)
            self.dropdown_to_func[self.opened_dd]()
            self.opened_dd = None
            return

        # Register an opened dropdown
        for dropdown in self.dropdowns:
            if dropdown.is_clicked_by(click_position):
                dropdown.handle_click(click_position)

                if dropdown.is_open():
                    self.opened_dd = dropdown
                    self.register_selected_reward(
                        ["dropdown_opened", self.dropdowns_to_str[dropdown]])
                return

        for checkbox in self.font_style_checkboxes:
            if checkbox.is_clicked_by(click_position):
                checkbox.handle_click(click_position)
                return

        if self.rbg.is_clicked_by(click_position):
            # Clicked button in the button group may have an additional action (e.g. a popup is
            # opened when this button is clicked)
            previous_color = self.rbg.get_value()

            self.rbg.handle_click(click_position)

            new_color = self.rbg.get_value()

            # Only change the selected color if a new color was selected. Important, otherwise a reward is
            # given, even if no color has been changed
            if previous_color != new_color:
                self.text_printer.set_color(new_color)

    def is_popup_open(self) -> int:
        return self.popup.is_open()

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        return img

    def get_clickable_elements(self, clickable_elements: List[Clickable]) -> List[Clickable]:
        if self.popup.is_open():
            return self.popup.get_clickable_elements()

        if self.opened_dd is not None:
            return self.opened_dd.get_visible_items()

        clickable_elements.extend(self.dropdowns)
        clickable_elements.extend(self.rbg.get_radio_buttons())
        clickable_elements.extend(self.font_style_checkboxes)

        return clickable_elements


class TextPrinterSettingsPopup(Page, RewardElement):
    """Popup for the text-printer settings (pops up when the green radio-button is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    STATE_LEN = 1
    CLICKABLE_ELEMENTS = 2

    BOUNDING_BOX = BoundingBox(99, 94, 210, 100)
    IMG_PATH = get_image_path(IMAGES_PATH, "text_printer_settings_popup.png")

    YES_BUTTON_BB = BoundingBox(121, 150, 80, 22)
    NO_BUTTON_BB = BoundingBox(207, 150, 80, 22)

    def __init__(self, text_printer_settings: TextPrinterSettings):
        Page.__init__(self, self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        RewardElement.__init__(self)

        self.settings = text_printer_settings

        self.yes_button: Button = Button(
            self.YES_BUTTON_BB, lambda: self.set_rb_and_close(True))
        self.no_button: Button = Button(
            self.NO_BUTTON_BB, lambda: self.set_rb_and_close(False))

    @property
    def reward_template(self):
        return {
            "popup": ["open", "close"],
            "popup_selection_button": [False, True]
        }

    def set_rb_and_close(self, selected: bool) -> None:
        if selected:
            self.settings.set_selected_rb(self.settings.green_rb)
        self.close()

        self.register_selected_reward(["popup_selection_button", selected])

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes_button.is_clicked_by(click_position):
            self.yes_button.handle_click(click_position)
            return

        if self.no_button.is_clicked_by(click_position):
            self.no_button.handle_click(click_position)

    def open(self):
        """Opens this popup."""
        self.get_state()[0] = 1

        self.register_selected_reward(["popup", "open"])

    def close(self):
        """Closes this popup."""
        self.get_state()[0] = 0

        self.register_selected_reward(["popup", "close"])

    def is_open(self) -> int:
        """Returns the opened-state of this popup."""
        return self.get_state()[0]

    def get_clickable_elements(self) -> List[Clickable]:
        return [self.yes_button, self.no_button]
