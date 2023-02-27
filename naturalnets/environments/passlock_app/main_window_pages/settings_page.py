import logging
import os
from typing import List

import numpy as np

from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.constants import ORANGE_COLOR
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.state_element import StateElement
from naturalnets.environments.gui_app.widgets.button import (
    Button, ShowPasswordButton)
from naturalnets.environments.passlock_app.constants import (IMAGES_PATH,
                                                             WINDOW_AREA_BB)
from naturalnets.environments.passlock_app.widgets.popup import PopUp
from naturalnets.environments.passlock_app.widgets.textfield import Textfield


class SettingsPage(Page, RewardElement):
    '''
    The settings page of the app.

    State Description:
    The Settings Page has no state itself, but it has a state for each of its widgets with a inherent state.
        0: The State of the auto_sync_button
        1: The State of the zoom_textfield
    '''

    ### CONSTANTS ###
    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "settings_page_img", "settings_page.png")
    CHANGE_COLOR_BB = BoundingBox(175, 275, 175, 60)
    SYNC_PW_BB = BoundingBox(175, 365, 300, 60)
    AUTO_SYNC_BB = BoundingBox(1780, 480, 100, 60)
    ZOOM_TEXTFIELD_BB = BoundingBox(1770, 580, 100, 60)
    ABOUT_BB = BoundingBox(175, 728, 265, 60)
    YT_BB = BoundingBox(175, 820, 265, 60)
    LOG_OUT_BB = BoundingBox(612, 930, 180, 50)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, WINDOW_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.change_color_button = Button(
            self.CHANGE_COLOR_BB, lambda: self.change_colour_popup.open_popup())
        self.sync_pw_button = Button(
            self.SYNC_PW_BB, lambda: self.sync_popup.open_popup())

        self.zoom_textfield = Textfield(
            self.ZOOM_TEXTFIELD_BB,
            lambda: self.enter_zoom_level, 
            ORANGE_COLOR
        )

        self.about_popup = SettingsPageAboutPopUp()
        self.sync_popup = SettingsPageSyncPopUp()
        self.change_colour_popup = SettingsPageChangeColourPopUp()

        self.auto_sync_onoffbutton = ShowPasswordButton(self.AUTO_SYNC_BB, None, ORANGE_COLOR)

        self.about_button = Button(
            self.ABOUT_BB, lambda: self.about_popup.open_popup())
        self.yt_button = Button(self.YT_BB, lambda: self.open_youtube_link)
        self.log_out_button = Button(self.LOG_OUT_BB, lambda: self.log_out())

        self.add_child(self.about_popup)
        self.add_child(self.sync_popup)
        self.add_child(self.change_colour_popup)

        self.set_reward_children(
            [self.about_popup, self.sync_popup, self.change_colour_popup])

        self.textfields: List[Textfield] = [self.zoom_textfield]

        self.buttons: List[Button] = [self.change_color_button,
                                      self.sync_pw_button,
                                      self.about_button,
                                      self.yt_button,
                                      self.log_out_button, self.auto_sync_onoffbutton]

        self.clickables = self.textfields + self.buttons

        self.reward_widgets_to_str = {
            self.auto_sync_onoffbutton: "auto_sync_onoffbutton",
            self.zoom_textfield: "zoom_textfield"
        }

        self.add_widget(self.auto_sync_onoffbutton)
        self.add_widget(self.zoom_textfield)

        logging.debug("SettingsPage created")

    @property
    def reward_template(self):
        '''
        Returns the reward template for the page.
        '''
        return {
            "auto_sync_onoffbutton": [False, True],
            "zoom_textfield": [False, True]
        }

    def enter_zoom_level(self):
        '''
        Enters the zoom level. Currently not implemented.
        '''
        logging.debug("Enter zoom level")
        

    def is_popup_open(self) -> bool:
        '''
        Returns True if a popup is open.
        '''
        return self.about_popup.is_open() or self.sync_popup.is_open() or self.change_colour_popup.is_open()
 

    def get_open_popup(self) -> PopUp:
        '''
        Returns the open popup.
        '''
        if self.about_popup.is_open():
            return self.about_popup

        if self.sync_popup.is_open():
            return self.sync_popup

        if self.change_colour_popup.is_open():
            return self.change_colour_popup

    def render(self, img) -> np.ndarray:
        """
        Renders the page onto the given image. 

        args: img - the image to render onto
        returns: the rendered image
        """
        if (self.is_popup_open()):
            img = self.get_open_popup().render(img)
            return img

        img = super().render(img)
        return img

    def reset(self):
        '''
        Resets the page.
        '''
        self.about_popup.reset()
        self.change_colour_popup.reset()
        self.sync_popup.reset()

    def handle_click(self, click_position: np.ndarray) -> bool:
        '''
        Handles a click on the page.

        args: click_position - the position of the click
        returns: True if the logout button was clicked and the page should be closed
        '''

        if (self.is_popup_open()):
            self.get_open_popup().handle_click(click_position)
            return False

        for clickable in self.clickables:
            if clickable.is_clicked_by(click_position):

                # If the logout button is clicked, return True
                if (clickable == self.log_out_button):
                    clickable.handle_click(click_position)
                    return True
                # If the clickable has a selected state, register the reward when it is selected
                elif (isinstance(clickable, StateElement)):
                    self.register_selected_reward(
                        [self.reward_widgets_to_str[clickable], clickable.is_selected()])

                clickable.handle_click(click_position)
                return False

    def open_youtube_link(self):
        '''
        Opens the youtube link. Currently not implemented.
        '''
        logging.debug("Open youtube link")

    def log_out(self):
        '''
        Logs out. Currently not implemented.'''
        logging.debug("Log out")


class SettingsPageChangeColourPopUp(PopUp):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    IMG_PATH = os.path.join(
        IMAGES_PATH, "settings_page_img", "settings_page_colour_popup.png")
    BOUNDING_BOX = BoundingBox(710, 425, 500, 150)

    def __init__(self):
        super().__init__(WINDOW_AREA_BB, self.IMG_PATH)

        logging.debug("SettingsPageChangeColourPopUp created")


class SettingsPageSyncPopUp(PopUp):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """
    BOUNDING_BOX = BoundingBox(650, 340, 615, 325)
    IMG_PATH = os.path.join(
        IMAGES_PATH, "settings_page_img", "settings_page_sny_popup.png")

    def __init__(self):
        super().__init__(WINDOW_AREA_BB, self.IMG_PATH)

        logging.debug("SettingsPageSyncPopUp created")


class SettingsPageAboutPopUp(PopUp):
    """Popup for the calculator settings (pops up when no operator-checkbox is selected).

       State description:
            state[0]: the opened-state of this popup.
    """

    BOUNDING_BOX = BoundingBox(650, 305, 615, 395)
    IMG_PATH = os.path.join(
        IMAGES_PATH, "settings_page_img", "settings_page_about_popup.png")

    def __init__(self):
        super().__init__(WINDOW_AREA_BB, self.IMG_PATH)

        logging.debug("SettingsPageAboutPopUp created")
