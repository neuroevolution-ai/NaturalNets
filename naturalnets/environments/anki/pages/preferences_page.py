import os
import random
import string
from typing import List
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH, AnkiLanguages, DeckAddType, VideoDriver
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
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
    
    SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB = BoundingBox(426, 227, 18, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB = BoundingBox(426, 263, 18, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB = BoundingBox(426, 301, 18, 9)

    NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB = BoundingBox(41, 150, 16, 16)
    NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB = BoundingBox(41, 183, 16, 16)
    NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB = BoundingBox(41, 218, 16, 16)
    NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB = BoundingBox(41, 251, 16, 16)
    NETWORK_WINDOW_MEDIA_LOG_BB = BoundingBox(44, 311, 91, 26)

    BACKUPS_WINDOW_INCREMENT_BB = BoundingBox(139, 153, 18, 9)
    BACKUPS_WINDOW_DECREMENT_BB = BoundingBox(139, 162, 18, 9)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PreferencesPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.PREFERENCES_BASIC_IMG_PATH)
        RewardElement.__init__(self)

        self.secure_random = random.SystemRandom()
        self.current_search_text = None        
        
        self.backup_number = 50
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
        self.basic_window_voice_recorder_qt_ddi = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)
        self.basic_window_voice_recorder_py_audio_ddi = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)

        self.basic_window_language_dd = Dropdown(self.BASIC_WINDOW_DD_1_BB, [self.basic_window_english_ddi, self.basic_window_german_ddi, self.basic_window_spanish_ddi])
        self.basic_window_video_driver_dd = Dropdown(self.BASIC_WINDOW_DD_2_BB, [self.basic_window_video_driver_opengl_ddi, self.basic_window_video_driver_angle_ddi, self.basic_window_video_driver_software_ddi])
        self.basic_window_add_to_deck_dd = Dropdown(self.BASIC_WINDOW_DD_3_BB, [self.basic_window_add_to_current_ddi,self.basic_window_change_deck_ddi])
        self.basic_window_voice_recorder_dd = Dropdown(self.BASIC_WINDOW_DD_4_BB, [self.basic_window_voice_recorder_qt_ddi,self.basic_window_voice_recorder_py_audio_ddi])
        
        self.basic_window_show_play_buttons_checkbox = CheckBox(self.BASIC_WINDOW_1_BB, self.register_selected_reward(["basic_window_show_play_buttons_checkbox"]))
        self.basic_window_interrupt_audio_checkbox = CheckBox(self.BASIC_WINDOW_2_BB, self.register_selected_reward(["basic_window_interrupt_audio_checkbox"]))
        self.basic_window_paste_clipboard_images_checkbox = CheckBox(self.BASIC_WINDOW_3_BB, self.register_selected_reward(["basic_window_paste_clipboard_images_checkbox"]))
        self.basic_window_paste_without_shift_key_checkbox = CheckBox(self.BASIC_WINDOW_4_BB, self.register_selected_reward(["basic_window_paste_without_shift_key_checkbox"]))
        self.basic_window_night_mode_checkbox = CheckBox(self.BASIC_WINDOW_5_BB)
        
        self.basic_window_put_text_button = Button(self.BASIC_WINDOW_SEARCH_TEXT_BB, self.set_current_search_text())
        self.basic_window_user_interface_increment_button = Button(self.BASIC_WINDOW_USER_INTERFACE_INCREMENT, self.increment_user_interface())
        self.basic_window_user_interface_decrement_button = Button(self.BASIC_WINDOW_USER_INTERFACE_DECREMENT, self.decrement_user_interface())

        self.basic_window_widgets: List[Widget] = [self.basic_window_language_dd,self.basic_window_video_driver_dd,self.basic_window_show_play_buttons_checkbox,
        self.basic_window_interrupt_audio_checkbox,self.basic_window_paste_clipboard_images_checkbox,self.basic_window_paste_without_shift_key_checkbox,
        self.basic_window_night_mode_checkbox,self.basic_window_add_to_deck_dd,self.basic_window_put_text_button,self.basic_window_user_interface_increment_button,
        self.basic_window_user_interface_decrement_button]

        self.scheduling_window_show_next_review_time_checkbox = CheckBox(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB, self.register_selected_reward(["scheduling_window_show_next_review_time_checkbox"]))
        self.scheduling_window_remaining_card_count_checkbox = CheckBox(self.SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB, self.register_selected_reward(["scheduling_window_remaining_card_count_checkbox"]))
        self.scheduling_window_legacy_timezone_checkbox = CheckBox(self.SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB, self.register_selected_reward(["scheduling_window_legacy_timezone_checkbox"]))
        self.scheduling_window_v3_scheduler_checkbox = CheckBox(self.SCHEDULING_WINDOW_V3_SCHEDULER_BB, self.register_selected_reward(["scheduling_window_v3_scheduler_checkbox"]))
        
        self.scheduling_window_next_day_increment_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB, self.increment_next_day())
        self.scheduling_window_learn_ahead_increment_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB, self.increment_learn_ahead())
        self.scheduling_window_timebox_time_increment_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB, self.increment_timebox_time())
        self.scheduling_window_next_day_decrement_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB, self.decrement_next_day())
        self.scheduling_window_learn_ahead_decrement_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB, self.decrement_learn_ahead())
        self.scheduling_window_timebox_time_decrement_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB, self.decrement_timebox_time())

        self.scheduling_window_widgets: List[Widget] = [self.scheduling_window_show_next_review_time_checkbox,self.scheduling_window_remaining_card_count_checkbox,
        self.scheduling_window_legacy_timezone_checkbox,self.scheduling_window_v3_scheduler_checkbox,self.scheduling_window_next_day_increment_button,
        self.scheduling_window_learn_ahead_increment_button,self.scheduling_window_timebox_time_increment_button,self.scheduling_window_next_day_decrement_button,
        self.scheduling_window_learn_ahead_decrement_button,self.scheduling_window_timebox_time_decrement_button]

        self.network_window_synchronize_audio_and_image_checkbox = CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB, self.register_selected_reward(["network_window_synchronize_audio_and_image_checkbox", not(self.network_window_synchronize_audio_and_image_checkbox.is_selected())]))
        self.network_window_synchronize_on_profile_checkbox = CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB, self.register_selected_reward(["network_window_synchronize_on_profile_checkbox", not(self.network_window_synchronize_on_profile_checkbox.is_selected())]))
        self.network_window_periodically_synchronize_checkbox = CheckBox(self.NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB, self.register_selected_reward(["network_window_periodically_synchronize_checkbox", not(self.network_window_periodically_synchronize_checkbox.is_selected())]))
        self.network_window_force_changes_in_one_direction_checkbox = CheckBox(self.NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB, self.register_selected_reward(["network_window_force_changes_in_one_direction_checkbox", not(self.network_window_force_changes_in_one_direction_checkbox.is_selected())]))
        self.network_window_media_log_button = Button(self.NETWORK_WINDOW_MEDIA_LOG_BB, self.register_selected_reward(["network_window_media_log_button"]))

        self.network_window_widgets: List[Widget] = [self.network_window_synchronize_audio_and_image_checkbox,self.network_window_synchronize_on_profile_checkbox,
        self.network_window_periodically_synchronize_checkbox,self.network_window_force_changes_in_one_direction_checkbox,self.network_window_media_log_button]

        self.backups_window_increment_backups = Button(self.BACKUPS_WINDOW_INCREMENT_BB, self.increment_backup_number())
        self.backups_window_decrement_backups = Button(self.BACKUPS_WINDOW_DECREMENT_BB, self.decrement_backup_number())
        self.backups_window_widgets: List[Widget] = [self.backups_window_increment_backups, self.backups_window_decrement_backups]

        self.dropdowns_to_str = {
            self.basic_window_language_dd: "basic_window_language_dd",
            self.basic_window_video_driver_dd: "basic_window_video_driver_dd",
            self.basic_window_add_to_deck_dd: "basic_window_add_to_deck_dd",
            self.basic_window_voice_recorder_dd: "basic_window_voice_recorder_dd",
        }

    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            
            "help": 0,
            "basic_switch_button" : 0,
            "scheduling_switch_button" : 0,
            "network_switch_button" : 0,
            "backup_switch_button" : 0,

            "basic_window_show_play_buttons_checkbox" : [True,False],
            "basic_window_interrupt_audio_checkbox": [True,False],
            "basic_window_paste_clipboard_images_checkbox": [True,False],
            "basic_window_paste_without_shift_key_checkbox": [True,False],
            "basic_window_night_mode_checkbox": [True,False],
            
            "basic_window_language_dd" : {
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.basic_window_language_dd.get_all_items()]
            },
            "basic_window_video_driver_dd" : {
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.basic_window_video_driver_dd.get_all_items()]
            },
            "basic_window_add_to_deck_dd" : {
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.basic_window_add_to_deck_dd.get_all_items()]
            },
            "basic_window_voice_recorder_dd" : {
                "opened": 0,
                "selected": [ddi.display_name for ddi in self.basic_window_voice_recorder_dd.get_all_items()]
            },

            "basic_window_user_interface_increment_button": 0,
            "basic_window_user_interface_decrement_button": 0,
            "basic_window_put_text_button": 0,

            "scheduling_window_show_next_review_time_checkbox": [True,False],
            "scheduling_window_remaining_card_count_checkbox": [True,False],
            "scheduling_window_legacy_timezone_checkbox": [True,False],
            "scheduling_window_v3_scheduler_checkbox": [True,False],
            
            "scheduling_window_next_day_increment_button": 0,
            "scheduling_window_learn_ahead_increment_button": 0,
            "scheduling_window_timebox_time_increment_button": 0,
            "scheduling_window_next_day_decrement_button": 0,
            "scheduling_window_learn_ahead_decrement_button": 0,
            "scheduling_window_timebox_time_decrement_button": 0,

            "network_window_synchronize_audio_and_image_checkbox": [True,False],
            "network_window_synchronize_on_profile_checkbox": [True,False],
            "network_window_periodically_synchronize_checkbox": [True,False],
            "network_window_force_changes_in_one_direction_checkbox": [True,False],
            "network_window_media_log_button": 0,

            "backups_window_increment_backups": 0,
            "backups_window_decrement_backups": 0
        }

    def set_state(self,index: int,value: int):
        self.get_state()[index] = value

    def increment_backup_number(self):
        if (self.backup_number < 100):
            self.backup_number += 1
            self.register_selected_reward(["backups_window_increment_backups"])

    def decrement_backup_number(self):
        if (self.backup_number > 0):
            self.backup_number -= 1
            self.register_selected_reward(["backups_window_decrement_backups"])

    def handle_click(self,click_position: np.ndarray):
        if(self.basic_switch_button.is_clicked_by(click_position)):
            self.basic_switch_button.handle_click(click_position)
            self.register_selected_reward(["basic_switch_button"])
        elif(self.scheduling_switch_button.is_clicked_by(click_position)):
            self.scheduling_switch_button.handle_click(click_position)
            self.register_selected_reward(["scheduling_switch_button"])
        elif(self.network_switch_button.is_clicked_by(click_position)):
            self.network_switch_button.handle_click(click_position)
            self.register_selected_reward(["network_switch_button"])
        elif(self.backup_switch_button.is_clicked_by(click_position)):
            self.backup_switch_button.handle_click(click_position)
            self.register_selected_reward(["backup_switch_button"])
        else:
            self.handle_click_by_open_window(click_position)
        
    def handle_click_by_open_window(self,click_position: np.ndarray):
        if (self.get_state()[1] == 1):
            self.handle_click_basic_window(click_position)
        elif (self.get_state()[2] == 1):
            self.handle_click_scheduling_window(click_position)
        elif (self.get_state()[3] == 1):
            self.handle_click_network_window(click_position)
        elif (self.get_state()[4] == 1):
            self.handle_click_backups_window(click_position)
    
    def handle_click_basic_window(self,click_position: np.ndarray):
        for widget in self.basic_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
                if isinstance(widget,Dropdown):
                    self.register_selected_reward(self.dropdowns_to_str[widget],"opened")
                    self.register_selected_reward(self.dropdowns_to_str[widget],"selected", widget.get_selected_item().display_name) 
                    
                
    def handle_click_scheduling_window(self,click_position: np.ndarray):
        for widget in self.scheduling_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
    
    def handle_click_network_window(self,click_position: np.ndarray):
        for widget in self.network_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
        
    def handle_click_backups_window(self,click_position: np.ndarray):
        for widget in self.backups_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
    
    def increment_user_interface(self):
        if (self.user_interface < 200):
            self.user_interface += 5
            self.register_selected_reward(["basic_window_user_interface_increment_button"])

    def decrement_user_interface(self):
        if (self.user_interface > 50):
            self.user_interface -= 5
            self.register_selected_reward(["basic_window_user_interface_decrement_button"])
    
    def increment_next_day(self):
        if (self.next_day < 10):
            self.next_day += 1
            self.register_selected_reward(["scheduling_window_next_day_increment_button"])
    
    def decrement_next_day(self):
        if (self.next_day > 0):
            self.next_day -= 1
            self.register_selected_reward(["scheduling_window_next_day_decrement_button"])
    
    def increment_learn_ahead(self):
        if (self.learn_ahead < 40):
            self.learn_ahead += 1
            self.register_selected_reward(["scheduling_window_learn_ahead_increment_button"])
    
    def decrement_learn_ahead(self):
        if (self.learn_ahead > 0):
            self.learn_ahead -= 1
            self.register_selected_reward(["scheduling_window_learn_ahead_decrement_button"])
    
    def increment_timebox_time(self):
        if (self.timebox_time < 20):
            self.timebox_time += 1
            self.register_selected_reward(["scheduling_window_timebox_time_increment_button"])

    def decrement_timebox_time(self):
        if (self.timebox_time > 0):
            self.timebox_time -= 1
            self.register_selected_reward(["scheduling_window_timebox_time_decrement_button"])

    def set_current_search_text(self):
        self.current_search_text = self.secure_random.choices(string.ascii_lowercase + string.digits, 10)
        self.register_selected_reward(["basic_window_put_text_button"])

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