import os
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH, AnkiLanguages, DeckAddType, VideoDriver
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class PreferencesPage(RewardElement,Page):
    
    """
    State description:
            state[0]: if this window is open
            state[j]: i-th sub-window is selected j = {1,2,3,4}  
    """
    
    WINDOW_BB = BoundingBox(10, 10, 798, 601)
    STATE_LEN = 5
    
    PREFERENCES_BASIC_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_basic.png")
    PREFERENCES_SCHEDULING_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_scheduling.png")
    PREFERENCES_NETWORK_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_network.png")
    PREFERENCES_BACKUP_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_backup.png")

    CLOSE_BB = BoundingBox(603, 607, 92, 26)
    HELP_BB = BoundingBox(705, 607, 92, 26)
    
    BASIC_SWITCH_BB = BoundingBox(25, 63, 61, 23)
    SCHEDULING_SWITCH_BB = BoundingBox(84, 63, 89, 23)
    NETWORK_SWITCH_BB = BoundingBox(173, 63, 77, 23)
    BACKUP_SWITCH_BB = BoundingBox(248, 607, 75, 23)

    BASIC_WINDOW_DD_1_BB = BoundingBox(42, 67, 734, 26)
    BASIC_WINDOW_DD_2_BB = BoundingBox(42, 108, 734, 26)
    BASIC_WINDOW_DD_3_BB = BoundingBox(42, 328, 734, 26)
    BASIC_WINDOW_DD_4_BB = BoundingBox(42, 367, 734, 26)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PreferencesPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.PREFERENCES_BASIC_IMG_PATH)
        RewardElement.__init__(self)

        self.close_button = Button(self.CLOSE_BB, self.close())
        self.help_button = Button(self.HELP_BB, self.help())
        
        self.basic_switch_button = Button(self.BASIC_SWITCH_BB, self.set_state(1,1))
        self.scheduling_switch_button = Button(self.SCHEDULING_SWITCH_BB, self.set_state(2,1))
        self.network_switch_button = Button(self.NETWORK_SWITCH_BB, self.set_state(3,1))
        self.backup_switch_button = Button(self.BACKUP_SWITCH_BB, self.set_state(4,1))
        
        self.basic_window_english_ddi = DropdownItem(AnkiLanguages.ENGLISH, AnkiLanguages.ENGLISH.value)
        self.basic_window_german_ddi = DropdownItem(AnkiLanguages.GERMAN, AnkiLanguages.GERMAN.value)
        self.basic_window_spanish_ddi = DropdownItem(AnkiLanguages.SPANISH, AnkiLanguages.SPANISH.value)

        self.basic_window_video_driver_opengl_ddi = DropdownItem(VideoDriver.OPENGL, VideoDriver.OPENGL.value)
        self.basic_window_video_driver_angle_ddi = DropdownItem(VideoDriver.ANGLE, VideoDriver.ANGLE.value)
        self.basic_window_video_driver_software_ddi = DropdownItem(VideoDriver.SOFTWARE, VideoDriver.SOFTWARE.value)

        self.basic_window_add_to_current_ddi = DropdownItem(DeckAddType.ADD_TO_CURRENT,DeckAddType.ADD_TO_CURRENT.value)
        self.basic_window_change_deck_ddi = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)

        self.basic_window_voice_recorder_qt = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)
        self.basic_window_voice_recorder_py_audio = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)

        self.basic_window_language_dd = Dropdown(self.BASIC_WINDOW_DD_1_BB, [self.basic_window_english_ddi, self.basic_window_german_ddi, self.basic_window_spanish_ddi])
        self.basic_window_video_driver_dd = Dropdown(self.BASIC_WINDOW_DD_2_BB, [self.basic_window_video_driver_opengl_ddi, self.basic_window_video_driver_angle_ddi, self.basic_window_video_driver_software_ddi])
        self.basic_window_show_play_buttons_checkbox
        self.basic_window_interrupt_audio_checkbox
        self.basic_window_paste_clipboard_images_checkbox
        self.basic_window_paste_without_shift_key_checkbox
        self.basic_window_night_mode_checkbox
        self.basic_window_add_to_deck_dd = Dropdown(self.BASIC_WINDOW_DD_3_BB, [self.basic_window_add_to_current_ddi,self.basic_window_change_deck_ddi])
        self.basic_window_voice_recorder_dd = Dropdown(self.BASIC_WINDOW_DD_4_BB, [self.basic_window_voice_recorder_qt,self.basic_window_voice_recorder_py_audio])
        self.basic_window_put_text_button

    @property
    def reward_template(self):
        return {
            "help": 0,
            "window": ["open","close"]
        }

    def set_state(self,index: int,value: int):
        self.get_state()[index] = value

    def handle_click(self,click_position: np.ndarray):
        if(self.basic_switch_button.is_clicked_by(click_position)):
            self.basic_switch_button.handle_click(click_position)
        elif(self.scheduling_switch_button.is_clicked_by(click_position)):
            self.scheduling_switch_button.handle_click(click_position)
        elif(self.network_switch_button.is_clicked_by(click_position)):
            self.network_switch_button.handle_click(click_position)
        elif(self.backup_switch_button.is_clicked_by(click_position)):
            self.backup_switch_button.handle_click(click_position)
        

    def help(self):
        print("Led to external website")
        self.register_selected_reward(["help"])

    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window","open"])
    
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window","close"])
    
    def is_open(self):
        return self.get_state()[0]

    def render(self,img: np.ndarray):
        if (self.get_state()[1]):
            to_render = cv2.imread(self.PREFERENCES_BASIC_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
        
        elif (self.get_state()[2]):
            to_render = cv2.imread(self.PREFERENCES_SCHEDULING_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
        
        elif (self.get_state()[3]):
            to_render = cv2.imread(self.PREFERENCES_NETWORK_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
        
        elif (self.get_state()[4]):
            to_render = cv2.imread(self.PREFERENCES_BACKUP_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
        
        return img