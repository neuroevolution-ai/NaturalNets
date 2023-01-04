from ast import List
import os
from naturalnets.environments.gui_app import widgets
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton, RadioButtonGroup
from naturalnets.environments.passlock_app.constants import IMAGES_PATH
from naturalnets.environments.passlock_app.constants import MAIN_PAGE_AREA_BB

class SettingsPage(Page, RewardElement):

    STATE_LEN = 0
    IMG_PATH = os.path.join(IMAGES_PATH, "calculator.png")

    CHANGE_COLOR_BB = BoundingBox(9, 112, 99, 22)
    SYNC_PW_BB = BoundingBox(9, 112, 99, 22)
    AUTO_SYNC_BB = BoundingBox(9, 112, 99, 22)
    ZOOM_TEXTFIELD_BB = BoundingBox(125, 316, 97, 22)
    ABOUT_BB = BoundingBox(9, 112, 99, 22)
    YT_BB = BoundingBox(9, 112, 99, 22)
    LOG_OUT_BB = BoundingBox(9, 112, 99, 22)

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.change_color_button = Button(self.CHANGE_COLOR_BB)
        self.sync_pw_button = Button(self.SYNC_PW_BB)

        self.zoom_radiobutton = RadioButton(
            self.ZOOM_TEXTFIELD_BB,
            self.enter_zoom_level()
        )
        
        self.auto_sync_radiobutton = RadioButton(self.AUTO_SYNC_BB)

        self.about_button = Button(self.ABOUT_BB)
        self.yt_button = Button(self.YT_BB)
        self.log_out_button = Button(self.LOG_OUT_BB)

        self.radio_button_group = RadioButtonGroup(self.auto_sync_radiobutton, self.zoom_radiobutton)

        self.widgets: List[Widget] = [
            self.change_color_button,
            self.sync_pw_button,
            self.radio_button_group,
            self.about_button,
            self.yt_button,
            self.log_out_button
        ]

        self.add_widgets(self.widgets)

    def enter_zoom_level(self):
        pass

    def render(self):
        pass

    def reset(self):
        pass
        
