from ntpath import join
from tabnanny import check
from typing import Dict, List, Tuple
import numpy as np

from enum import Enum
from naturalnets.environments.app.bounding_box import BoundingBox
from naturalnets.environments.app.colors import Color
from naturalnets.environments.app.constants import IMAGES_PATH, SETTINGS_AREA_BB
from naturalnets.environments.app.interfaces import HasPopups
from naturalnets.environments.app.main_window import MainWindow
from naturalnets.environments.app.main_window_pages.figure_printer import Figure
from naturalnets.environments.app.page import Page
from naturalnets.environments.app.widgets.button import Button
from naturalnets.environments.app.widgets.check_box import CheckBox
from naturalnets.environments.app.widgets.dropdown import Dropdown, DropdownItem
from naturalnets.environments.app.widgets.radio_button_group import RadioButton, RadioButtonGroup


class FigurePrinterSettings(Page):
    STATE_LEN = 0
    IMG_PATH = IMAGES_PATH + "figure_printer_settings.png"

    SHOW_FIG_PRINTER_BB = BoundingBox(38, 91, 141, 14)
    
    # figure checkboxes bounding-boxes
    CHRISTMAS_TREE_BB = BoundingBox(38, 145, 103, 14)
    SPACE_SHIP_BB = BoundingBox(217, 145, 83, 14)
    GUITAR_BB = BoundingBox(38, 171, 54, 14)
    HOUSE_BB = BoundingBox(217, 171, 56, 14)

    # color_rbg bounding-boxes
    GREEN_RB_BB = BoundingBox(38, 225, 55, 14)
    BLUE_RB_BB = BoundingBox(38, 251, 47, 14)
    BLACK_RB_BB = BoundingBox(217, 225, 53, 14)
    BROWN_RB_BB = BoundingBox(217, 251, 57, 14)


    def __init__(self, main_window:MainWindow):
        super().__init__(self.STATE_LEN, SETTINGS_AREA_BB, self.IMG_PATH)
        self.main_window = main_window
        self.figure_printer = main_window.figure_printer

        self.figure_checkboxes_popup = FigureCheckboxesPopup(self)
        self.add_child(self.figure_checkboxes_popup)

        self._show_fig_printer_checkbox = CheckBox(self.SHOW_FIG_PRINTER_BB)

        self.add_widget(self._show_fig_printer_checkbox)

        self.figure_checkboxes, self.checkbox_to_figure = self._get_figure_checkboxes()
        self.figure_to_checkbox = {figure: checkbox for (checkbox, figure) in self.checkbox_to_figure.items()}
        self.add_widgets(self.figure_checkboxes)

        self._color_rbg, self._button_to_color = self._get_color_rbg()
        self.add_widget(self._color_rbg)

        self.figure_printer.set_figure_color(self.get_figure_color())

    def _get_figure_checkboxes(self) -> Tuple[List[CheckBox], Dict[CheckBox, Figure]]:
        figure_checkboxes = []
        christmas_tree_checkbox = CheckBox(self.CHRISTMAS_TREE_BB, 
            lambda is_checked : self.figure_printer.dropdown.set_visible(self.figure_printer.christmas_tree_ddi, is_checked))
        space_ship_checkbox = CheckBox(self.SPACE_SHIP_BB, 
            lambda is_checked: self.figure_printer.dropdown.set_visible(self.figure_printer.space_ship_ddi, is_checked))
        guitar_checkbox = CheckBox(self.GUITAR_BB, 
            lambda is_checked: self.figure_printer.dropdown.set_visible(self.figure_printer.guitar_ddi, is_checked))
        house_checkbox = CheckBox(self.HOUSE_BB, 
            lambda is_checked: self.figure_printer.dropdown.set_visible(self.figure_printer.house_ddi, is_checked))

        figure_checkboxes.append(christmas_tree_checkbox)
        figure_checkboxes.append(space_ship_checkbox)
        figure_checkboxes.append(guitar_checkbox)
        figure_checkboxes.append(house_checkbox)

        checkbox_to_figure = {
            christmas_tree_checkbox: Figure.CHRISTMAS_TREE,
            space_ship_checkbox: Figure.SPACE_SHIP,
            guitar_checkbox: Figure.GUITAR,
            house_checkbox: Figure.HOUSE,
        }

        christmas_tree_checkbox.set_selected(1)

        return figure_checkboxes, checkbox_to_figure

    def _get_color_rbg(self) -> Tuple[RadioButtonGroup, Dict[RadioButton, Color]]:
        black_rb = RadioButton(self.BLACK_RB_BB)
        green_rb = RadioButton(self.GREEN_RB_BB)
        blue_rb = RadioButton(self.BLUE_RB_BB)
        brown_rb = RadioButton(self.BROWN_RB_BB)

        button_to_color = {
            black_rb: Color.BLACK,
            green_rb: Color.GREEN,
            blue_rb: Color.BLUE,
            brown_rb: Color.BROWN
        }

        rbg = RadioButtonGroup([black_rb])
        rbg.add_radio_buttons([
            green_rb,
            blue_rb,
            brown_rb,
        ])

        return rbg, button_to_color

    def get_figure_color(self) -> Color:
        return self._button_to_color[self._color_rbg.get_selected_radio_button()]

    def get_figures(self) -> List[Figure]:
        selected_figures = []
        for checkbox in self.figure_checkboxes:
            if checkbox.is_selected():
                selected_figures.append(self.checkbox_to_figure[checkbox])

        return selected_figures
    
    def is_figure_printer_activated(self) -> bool:
        return self._show_fig_printer_checkbox.is_selected()

    def is_popup_open(self) -> bool:
        return self.figure_checkboxes_popup.is_open()

    def handle_click(self, click_position: np.ndarray = None) -> None:
        if self.figure_checkboxes_popup.is_open():
            self.figure_checkboxes_popup.handle_click(click_position)

        elif self._show_fig_printer_checkbox.is_clicked_by(click_position):
            self._show_fig_printer_checkbox.handle_click()
            self.main_window.set_figure_printer_button_visible(self._show_fig_printer_checkbox.is_selected())

            # change current main window page if it was the figure printer and the figure printer
            # has been deactivated
            if self.main_window.get_current_page() == self.main_window.figure_printer\
                    and not self._show_fig_printer_checkbox.is_selected():
                self.main_window.set_current_page(self.main_window.text_printer)

        # other widgets only available when figure printer is activated
        elif self.is_figure_printer_activated():
            if self._color_rbg.get_bb().is_point_inside(click_position):
                self._color_rbg.handle_click(click_position)
                self.figure_printer.set_figure_color(self.get_figure_color())
            else:
                for checkbox in self.figure_checkboxes:
                    if checkbox.is_clicked_by(click_position):
                        checkbox.handle_click(click_position)
                        break
                if self.get_selected_checkboxes_count() == 0:
                    self.figure_checkboxes_popup.open()

                
            #for widget in self.get_widgets():
            #    if widget.is_clicked_by(click_position):
            #        widget.handle_click(click_position)
    def get_selected_checkboxes_count(self):
        selected_cbx_count = 0
        for checkbox in self.figure_checkboxes:
            selected_cbx_count += checkbox.is_selected()
        return selected_cbx_count

    def select_figure_checkbox(self, figure:Figure):
        self.figure_to_checkbox[figure].set_selected(True)

    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.figure_checkboxes_popup.is_open():
            img = self.figure_checkboxes_popup.render(img)
        return img


class FigureCheckboxesPopup(Page):
    STATE_LEN = 1
    BOUNDING_BOX = BoundingBox(14, 87, 381, 114)
    IMG_PATH = IMAGES_PATH + "figure_settings_checkboxes_popup.png"

    APPLY_BUTTON_BB = BoundingBox(103, 157, 203, 22)
    DROPDOWN_BB = BoundingBox(36, 129, 337, 22) 

    def __init__(self, figure_printer_settings:FigurePrinterSettings):
        super().__init__(self.STATE_LEN, self.BOUNDING_BOX, self.IMG_PATH)
        self.apply_button = Button(self.APPLY_BUTTON_BB, lambda: self.close())
        self.figure_printer_settings = figure_printer_settings

        self.christmas_tree_ddi = DropdownItem(Figure.CHRISTMAS_TREE)
        space_ship_ddi = DropdownItem(Figure.SPACE_SHIP)
        guitar_ddi = DropdownItem(Figure.GUITAR)
        house_ddi = DropdownItem(Figure.HOUSE)
        ddis = [self.christmas_tree_ddi, space_ship_ddi, guitar_ddi, house_ddi]
        self.dropdown = Dropdown(self.DROPDOWN_BB, ddis)
        self.add_child(self.dropdown)

    def handle_click(self, click_position: np.ndarray = None) -> None:
        # check dropdown first, may obscure apply-button when opened
        if self.dropdown.is_clicked_by(click_position) or self.dropdown.is_open():
            self.dropdown.handle_click(click_position)
        elif self.apply_button.is_clicked_by(click_position):
            self.apply_button.handle_click()
            curr_dropdown_value:Figure = self.dropdown.get_current_value()
            if curr_dropdown_value is not None:
                self.figure_printer_settings.select_figure_checkbox(curr_dropdown_value)
        #TODO
        pass

    def open(self):
        self.get_state()[0] = 1
        self.dropdown.set_selected_item(self.christmas_tree_ddi)

    def close(self):
        self.get_state()[0] = 0

    def is_open(self):
        return self.get_state()[0]

    def render(self, img: np.ndarray):
        if self.is_open():
            img = super().render(img)
            if self.dropdown.is_open():
                img = self.dropdown.render(img)
        return img