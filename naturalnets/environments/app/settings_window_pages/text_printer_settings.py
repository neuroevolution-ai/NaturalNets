from ntpath import join
from tkinter.tix import IMAGE
import numpy as np

from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.enums import Font, FontStyle
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.main_window_pages.text_printer import TextPrinter
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.check_box import CheckBox
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.app.widgets.radio_button_group import RadioButton, RadioButtonGroup

class TextPrinterSettings(Page):
    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "text_printer_settings.png"

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



    def __init__(self, text_printer:TextPrinter):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self.text_printer = text_printer

        # init popup
        self.popup = TextPrinterSettingsPopup(self)

        # init font-style checkboxes
        self.bold = CheckBox(self.BOLD_BB, lambda is_checked: self.text_printer.set_font_style(FontStyle.BOLD, is_checked))
        self.italic = CheckBox(self.ITALIC_BB, lambda is_checked: self.text_printer.set_font_style(FontStyle.ITALIC, is_checked))
        self.underline = CheckBox(self.UNDERLINE_BB, lambda is_checked: self.text_printer.set_font_style(FontStyle.UNDERLINE, is_checked))
        self.font_style_checkboxes = [self.bold, self.italic, self.underline]
        self.add_widgets(self.font_style_checkboxes)

        # init dropdowns
        ## number of words dropdown
        self.n_words_50_ddi = DropdownItem(50, "50")
        self.n_words_100_ddi = DropdownItem(100, "100")
        self.n_words_200_ddi = DropdownItem(200, "200")
        self.n_words_400_ddi = DropdownItem(400, "400")
        self.n_words_ddis = [self.n_words_50_ddi, self.n_words_100_ddi, self.n_words_200_ddi, self.n_words_400_ddi]
        self.n_words_dd = Dropdown(self.N_WORDS_BB, self.n_words_ddis)
        self.n_words_dd.set_selected_item(self.n_words_50_ddi)
        ## font size dropdown
        self.font_size_12 = DropdownItem(12, "12")
        self.font_size_14 = DropdownItem(14, "14")
        self.font_size_16 = DropdownItem(16, "16")
        self.font_size_18 = DropdownItem(18, "18")
        self.font_size_20 = DropdownItem(20, "20")
        self.font_size_ddis = [self.font_size_12, self.font_size_14, self.font_size_16, self.font_size_18, self.font_size_20]
        self.font_size_dd = Dropdown(self.FONT_SIZE_BB, self.font_size_ddis)
        self.font_size_dd.set_selected_item(self.font_size_12)
        ## font dropdown #DejaVu Sans, Liberation Mono, Nimbus Roman, Ubuntu
        self.font_DS_ddi = DropdownItem(Font.DEJAVU_SANS, Font.DEJAVU_SANS.value)
        self.font_LM_ddi = DropdownItem(Font.LIBERATION_MONO, Font.LIBERATION_MONO.value)
        self.font_NR_ddi = DropdownItem(Font.NIMBUS_ROMAN, Font.NIMBUS_ROMAN.value)
        self.font_U_ddi = DropdownItem(Font.UBUNTU, Font.UBUNTU.value)
        self.font_ddis = [self.font_DS_ddi, self.font_LM_ddi, self.font_NR_ddi, self.font_U_ddi]
        self.fonts_dd = Dropdown(self.FONT_BB, self.font_ddis)
        self.fonts_dd.set_selected_item(self.font_DS_ddi)

        # n-words dropdown needs to be first since it may occlude the others when opened (important for iteration in handle_click)
        self.dropdowns:list[Dropdown] = [self.n_words_dd, self.font_size_dd, self.fonts_dd]
        self.dropdown_to_func = {self.n_words_dd: lambda : self.text_printer.set_n_words(self.n_words_dd.get_current_value()),
                                self.font_size_dd: lambda : self.text_printer.set_font_size(self.font_size_dd.get_current_value()),
                                self.fonts_dd: lambda : self.text_printer.set_font(self.fonts_dd.get_current_value())}
        self.add_widgets(self.dropdowns)

        # init radio button group
        self.red_rb = RadioButton(self.RED_RB_BB, value=Color.RED)
        self.green_rb = RadioButton(self.GREEN_RB_BB, value=Color.GREEN, action=lambda: self.popup.open())
        self.blue_rb = RadioButton(self.BLUE_RB_BB, value=Color.BLUE)
        self.black_rb = RadioButton(self.BLACK_RB_BB, value=Color.BLACK)
        self.rbg = RadioButtonGroup([self.black_rb, self.red_rb, self.green_rb, self.blue_rb])
        self.add_widget(self.rbg)

    def set_selected_rb(self, rb:RadioButton) -> None:
        """Sets the selected radio button.

        Args:
            rb (RadioButton): The radio button to select, must be in self.rbg
        """
        self.rbg.set_selected_button(rb)
        self.text_printer.set_color(rb.get_value())

    def is_dropdown_open(self) -> bool:
        return self._get_opened_dropdown() is not None

    def _get_opened_dropdown(self) -> Dropdown:
        for dropdown in self.dropdown_to_func.keys():
            if dropdown.is_open():
                return dropdown
        return None

    def handle_click(self, click_position: np.ndarray = None):
        if self.is_popup_open():
            self.popup.handle_click(click_position)
            return

        opened_dd = self._get_opened_dropdown()
        if opened_dd is not None:
            #TODO duplicate code here further down when handling dropdown clicks
            # => add action to dropdown items?
            old_value = opened_dd.get_current_value()
            opened_dd.handle_click(click_position)
            if old_value != opened_dd.get_current_value():
                self.dropdown_to_func[opened_dd]()
            return

        # handle dropdown clicks first, as they may occlude other widgets if opened
        for dropdown, func in self.dropdown_to_func.items():
            if dropdown.is_clicked_by(click_position):
                old_value = dropdown.get_current_value()
                dropdown.handle_click(click_position)
                if old_value != dropdown.get_current_value():
                    func()
                return
        
        for checkbox in self.font_style_checkboxes:
            if checkbox.is_clicked_by(click_position):
                checkbox.handle_click(click_position)
                return

        if self.rbg.is_clicked_by(click_position):
            self.rbg.handle_click(click_position)
            self.text_printer.set_color(self.rbg.get_value())

    def is_popup_open(self) -> bool:
        return self.popup.is_open()

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.popup.is_open():
            img = self.popup.render(img)
        return img

class TextPrinterSettingsPopup(Page):
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(99, 94, 210, 100)
    IMG_PATH = IMAGES_PATH + "text_printer_settings_popup.png"
    
    YES_BUTTON_BB = BoundingBox(121, 150, 80, 22)
    NO_BUTTON_BB = BoundingBox(207, 150, 80, 22)
    
    def __init__(self, text_printer_settings:TextPrinterSettings):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.settings = text_printer_settings

        self.yes:Button = Button(self.YES_BUTTON_BB, lambda: self.set_rb_and_close(True))
        self.no:Button = Button(self.NO_BUTTON_BB, lambda: self.set_rb_and_close(False))

    def set_rb_and_close(self, selected:bool) -> None:
        if selected:
            self.settings.set_selected_rb(self.settings.green_rb)
        self.close()

    def handle_click(self, click_position: np.ndarray) -> None:
        if self.yes.is_clicked_by(click_position):
            self.yes.handle_click()
            return
        elif self.no.is_clicked_by(click_position):
            self.no.handle_click()
        
    def open(self):
        self.get_state()[0] = 1

    def close(self):
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]
