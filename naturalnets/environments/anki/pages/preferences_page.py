import os
import random
import string
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH, AnkiLanguages, DeckAddType, VideoDriver
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
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

    BASIC_WINDOW_1_BB = BoundingBox(42, 150, 16, 16)
    BASIC_WINDOW_2_BB = BoundingBox(42, 186, 16, 16)
    BASIC_WINDOW_3_BB = BoundingBox(42, 222, 16, 16)
    BASIC_WINDOW_4_BB = BoundingBox(42, 258, 16, 16)
    BASIC_WINDOW_5_BB = BoundingBox(42, 294, 16, 16)

    BASIC_WINDOW_SEARCH_TEXT_BB = BoundingBox(690, 437, 87, 22)
    BASIC_WINDOW_USER_INTERFACE_INCREMENT = BoundingBox(199, 478, 18, 9)
    BASIC_WINDOW_USER_INTERFACE_DECREMENT = BoundingBox(199, 487, 18, 9)

    SCHEDULING_WINDOW_NEXT_REVIEW_TIME_BB = BoundingBox(37, 101, 16, 16)
    SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB = BoundingBox(37, 131, 16, 16)
    SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB = BoundingBox(37, 159, 16, 16)
    SCHEDULING_WINDOW_V3_SCHEDULER_BB = BoundingBox(37, 188, 16, 16)

    SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB = BoundingBox(426, 216, 18, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB = BoundingBox(426, 254, 18, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB = BoundingBox(426, 292, 18, 9)

    SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB = BoundingBox(426, 225, 18, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB = BoundingBox(426, 263, 18, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB = BoundingBox(426, 301, 18, 9)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PreferencesPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.PREFERENCES_BASIC_IMG_PATH)
        RewardElement.__init__(self)

        self.secure_random = random.SystemRandom()
        self.current_search_text = None        
        
        self.user_interface = 100
        self.next_day = 4
        self.learn_ahead = 20
        self.timebox_time = 5
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
        self.basic_window_show_play_buttons_checkbox = CheckBox(self.BASIC_WINDOW_1_BB)
        self.basic_window_interrupt_audio_checkbox = CheckBox(self.BASIC_WINDOW_2_BB)
        self.basic_window_paste_clipboard_images_checkbox = CheckBox(self.BASIC_WINDOW_3_BB)
        self.basic_window_paste_without_shift_key_checkbox = CheckBox(self.BASIC_WINDOW_4_BB)
        self.basic_window_night_mode_checkbox = CheckBox(self.BASIC_WINDOW_5_BB)
        self.basic_window_add_to_deck_dd = Dropdown(self.BASIC_WINDOW_DD_3_BB, [self.basic_window_add_to_current_ddi,self.basic_window_change_deck_ddi])
        self.basic_window_voice_recorder_dd = Dropdown(self.BASIC_WINDOW_DD_4_BB, [self.basic_window_voice_recorder_qt,self.basic_window_voice_recorder_py_audio])
        self.basic_window_put_text_button = Button(self.BASIC_WINDOW_SEARCH_TEXT_BB, self.set_current_search_text())
        self.basic_window_user_interface_increment_button = Button(self.BASIC_WINDOW_USER_INTERFACE_INCREMENT, self.increment_user_interface())
        self.basic_window_user_interface_decrement_button = Button(self.BASIC_WINDOW_USER_INTERFACE_DECREMENT, self.decrement_user_interface())

        self.basic_window_widgets = [self.basic_window_language_dd,self.basic_window_video_driver_dd,self.basic_window_show_play_buttons_checkbox,
        self.basic_window_interrupt_audio_checkbox,self.basic_window_paste_clipboard_images_checkbox,self.basic_window_paste_without_shift_key_checkbox,
        self.basic_window_night_mode_checkbox,self.basic_window_add_to_deck_dd,self.basic_window_put_text_button,self.basic_window_user_interface_increment_button,
        self.basic_window_user_interface_decrement_button]
        
        self.scheduling_window_show_next_review_time_checkbox = CheckBox(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB)
        self.scheduling_window_remaining_card_count_checkbox = CheckBox(self.SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB)
        self.scheduling_window_legacy_timezone_checkbox = CheckBox(self.SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB)
        self.scheduling_window_v3_scheduler_checkbox = CheckBox(self.SCHEDULING_WINDOW_V3_SCHEDULER_BB)
        
        self.scheduling_window_next_day_increment_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB, self.increment_next_day())
        self.scheduling_window_learn_ahead_increment_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB, self.increment_learn_ahead())
        self.scheduling_window_timebox_time_increment_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB, self.increment_timebox_time())
        self.scheduling_window_next_day_decrement_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB, self.decrement_next_day())
        self.scheduling_window_learn_ahead_decrement_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB, self.decrement_learn_ahead())
        self.scheduling_window_timebox_time_decrement_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB, self.decrement_timebox_time())

        self.scheduling_window_widgets = [self.scheduling_window_show_next_review_time_checkbox,self.scheduling_window_remaining_card_count_checkbox,
        self.scheduling_window_legacy_timezone_checkbox,self.scheduling_window_v3_scheduler_checkbox,self.scheduling_window_next_day_increment_button,
        self.scheduling_window_learn_ahead_increment_button,self.scheduling_window_timebox_time_increment_button,self.scheduling_window_next_day_decrement_button,
        self.scheduling_window_learn_ahead_decrement_button,self.scheduling_window_timebox_time_decrement_button]
        
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
        
    def increment_user_interface(self):
        if (self.user_interface < 200):
            self.user_interface += 5

    def decrement_user_interface(self):
        if (self.user_interface > 50):
            self.user_interface -= 5
    
    def increment_next_day(self):
        if (self.next_day < 10):
            self.next_day += 1
    
    def decrement_next_day(self):
        if (self.next_day > 0):
            self.next_day -= 1
    
    def increment_learn_ahead(self):
        if (self.learn_ahead < 40):
            self.learn_ahead += 1
    
    def decrement_learn_ahead(self):
        if (self.learn_ahead > 0):
            self.learn_ahead -= 1
    
    def increment_timebox_time(self):
        if (self.timebox_time < 20):
            self.timebox_time += 1

    def decrement_timebox_time(self):
        if (self.timebox_time > 0):
            self.timebox_time -= 1

    def set_current_search_text(self):
        self.current_search_text = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)

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