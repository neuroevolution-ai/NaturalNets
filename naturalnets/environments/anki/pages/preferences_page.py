import os
import random
import string
from typing import List
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH, AnkiLanguages, DeckAddType, VideoDriver, VoiceRecorder
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup_page import LeadsToExternalWebsitePopupPage
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb, put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem


class PreferencesPage(RewardElement,Page):
    
    """
    State description:
            state[0]: if this window is open
            state[j]: i-th sub-window is selected j = {1,2,3,4}  
    """
    
    WINDOW_BB = BoundingBox(10, 40, 801, 601)
    STATE_LEN = 5
    
    PREFERENCES_BASIC_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_basic.png")
    PREFERENCES_SCHEDULING_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_scheduling.png")
    PREFERENCES_NETWORK_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_network.png")
    PREFERENCES_BACKUP_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_backup.png")

    CLOSE_BB = BoundingBox(513, 601, 76, 23)
    HELP_BB = BoundingBox(601, 601, 76, 23)
    
    BASIC_SWITCH_BB = BoundingBox(22, 58, 62, 23)
    SCHEDULING_SWITCH_BB = BoundingBox(84, 58, 63, 23)
    NETWORK_SWITCH_BB = BoundingBox(147, 58, 63, 23)
    BACKUP_SWITCH_BB = BoundingBox(211, 58, 63, 23)

    BASIC_WINDOW_DD_1_BB = BoundingBox(35, 96, 734, 24)
    BASIC_WINDOW_DD_2_BB = BoundingBox(35, 138, 734, 24)
    BASIC_WINDOW_DD_3_BB = BoundingBox(35, 357, 734, 24)
    BASIC_WINDOW_DD_4_BB = BoundingBox(35, 396, 734, 24)

    BASIC_WINDOW_DD_1_BB_OFFSET = BoundingBox(35, 120, 734, 24)
    BASIC_WINDOW_DD_2_BB_OFFSET = BoundingBox(35, 162, 734, 24)
    BASIC_WINDOW_DD_3_BB_OFFSET = BoundingBox(35, 381, 734, 24)
    BASIC_WINDOW_DD_4_BB_OFFSET = BoundingBox(35, 420, 734, 24)

    BASIC_WINDOW_1_CHECKBOX_BB = BoundingBox(37, 180, 16, 16)
    BASIC_WINDOW_2_CHECKBOX_BB = BoundingBox(37, 216, 16, 16)
    BASIC_WINDOW_3_CHECKBOX_BB = BoundingBox(37, 252, 16, 16)
    BASIC_WINDOW_4_CHECKBOX_BB = BoundingBox(37, 288, 16, 16)
    BASIC_WINDOW_5_CHECKBOX_BB = BoundingBox(37, 325, 16, 16)

    BASIC_WINDOW_SEARCH_TEXT_BB = BoundingBox(586, 466, 74, 22)
    BASIC_WINDOW_USER_INTERFACE_INCREMENT = BoundingBox(170, 509, 18, 9)
    BASIC_WINDOW_USER_INTERFACE_DECREMENT = BoundingBox(170, 519, 18, 9)

    SCHEDULING_WINDOW_NEXT_REVIEW_TIME_BB = BoundingBox(33, 93, 16, 16)
    SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB = BoundingBox(33, 125, 16, 16)
    SCHEDULING_WINDOW_SHOW_LEARNING_CARDS_BB = BoundingBox(33, 151, 16, 16)
    SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB = BoundingBox(33, 181, 16, 16)
    SCHEDULING_WINDOW_V3_SCHEDULER_BB = BoundingBox(33, 209, 16, 16)

    SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB = BoundingBox(362, 268, 18, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB = BoundingBox(362, 308, 18, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB = BoundingBox(362, 346, 18, 9)
    
    SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB = BoundingBox(362, 278, 18, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB = BoundingBox(362, 318, 18, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB = BoundingBox(362, 356, 18, 9)

    NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB = BoundingBox(34, 144, 16, 16)
    NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB = BoundingBox(34, 176, 16, 16)
    NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB = BoundingBox(34, 210, 16, 16)
    NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB = BoundingBox(34, 245, 16, 16)

    BACKUPS_WINDOW_INCREMENT_BB = BoundingBox(117, 147, 18, 9)
    BACKUPS_WINDOW_DECREMENT_BB = BoundingBox(117, 157, 18, 9)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PreferencesPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.PREFERENCES_BASIC_IMG_PATH)
        RewardElement.__init__(self)
        self.get_state()[1] = 1
        self.leads_to_external_website_popup = LeadsToExternalWebsitePopupPage()
        self.current_search_text = None        
        self.open_dd = None

        self.backup_number = 50
        self.user_interface = 100
        self.next_day = 4
        self.learn_ahead = 20
        self.timebox_time = 5
        self.close_button = Button(self.CLOSE_BB, self.close)
        self.help_button = Button(self.HELP_BB, self.help)

        self.basic_switch_button = Button(self.BASIC_SWITCH_BB, self.set_basic)
        self.scheduling_switch_button = Button(self.SCHEDULING_SWITCH_BB, self.set_scheduling)
        self.network_switch_button = Button(self.NETWORK_SWITCH_BB, self.set_network)
        self.backup_switch_button = Button(self.BACKUP_SWITCH_BB, self.set_backup)
        
        self.basic_window_english_ddi = DropdownItem(AnkiLanguages.ENGLISH, AnkiLanguages.ENGLISH.value)
        self.basic_window_german_ddi = DropdownItem(AnkiLanguages.GERMAN, AnkiLanguages.GERMAN.value)
        self.basic_window_spanish_ddi = DropdownItem(AnkiLanguages.SPANISH, AnkiLanguages.SPANISH.value)

        self.basic_window_video_driver_opengl_ddi = DropdownItem(VideoDriver.OPENGL, VideoDriver.OPENGL.value)
        self.basic_window_video_driver_angle_ddi = DropdownItem(VideoDriver.ANGLE, VideoDriver.ANGLE.value)
        self.basic_window_video_driver_software_ddi = DropdownItem(VideoDriver.SOFTWARE, VideoDriver.SOFTWARE.value)

        self.basic_window_add_to_current_ddi = DropdownItem(DeckAddType.ADD_TO_CURRENT,DeckAddType.ADD_TO_CURRENT.value)
        self.basic_window_change_deck_ddi = DropdownItem(DeckAddType.CHANGE_DECK,DeckAddType.CHANGE_DECK.value)
        
        self.basic_window_voice_recorder_qt_ddi = DropdownItem(VoiceRecorder.PY_AUDIO, VoiceRecorder.PY_AUDIO.value)
        self.basic_window_voice_recorder_py_audio_ddi = DropdownItem(VoiceRecorder.QT, VoiceRecorder.QT.value)

        self.basic_window_language_dd = Dropdown(self.BASIC_WINDOW_DD_1_BB_OFFSET, [self.basic_window_english_ddi, self.basic_window_german_ddi, self.basic_window_spanish_ddi])
        self.basic_window_video_driver_dd = Dropdown(self.BASIC_WINDOW_DD_2_BB_OFFSET, [self.basic_window_video_driver_opengl_ddi, self.basic_window_video_driver_angle_ddi, self.basic_window_video_driver_software_ddi])
        self.basic_window_add_to_deck_dd = Dropdown(self.BASIC_WINDOW_DD_3_BB_OFFSET, [self.basic_window_add_to_current_ddi,self.basic_window_change_deck_ddi])
        self.basic_window_voice_recorder_dd = Dropdown(self.BASIC_WINDOW_DD_4_BB_OFFSET, [self.basic_window_voice_recorder_qt_ddi,self.basic_window_voice_recorder_py_audio_ddi])
        
        self.basic_window_show_play_buttons_checkbox = CheckBox(self.BASIC_WINDOW_1_CHECKBOX_BB)
        self.basic_window_interrupt_audio_checkbox = CheckBox(self.BASIC_WINDOW_2_CHECKBOX_BB)
        self.basic_window_paste_clipboard_images_checkbox = CheckBox(self.BASIC_WINDOW_3_CHECKBOX_BB)
        self.basic_window_paste_without_shift_key_checkbox = CheckBox(self.BASIC_WINDOW_4_CHECKBOX_BB)
        self.basic_window_night_mode_checkbox = CheckBox(self.BASIC_WINDOW_5_CHECKBOX_BB)
        
        self.basic_window_put_text_button = Button(self.BASIC_WINDOW_SEARCH_TEXT_BB, self.set_current_search_text)
        self.basic_window_user_interface_increment_button = Button(self.BASIC_WINDOW_USER_INTERFACE_INCREMENT, self.increment_user_interface)
        self.basic_window_user_interface_decrement_button = Button(self.BASIC_WINDOW_USER_INTERFACE_DECREMENT, self.decrement_user_interface)

        self.basic_window_widgets: List[Widget] = [self.basic_window_language_dd,self.basic_window_video_driver_dd,self.basic_window_show_play_buttons_checkbox,
        self.basic_window_interrupt_audio_checkbox,self.basic_window_paste_clipboard_images_checkbox,self.basic_window_paste_without_shift_key_checkbox,
        self.basic_window_night_mode_checkbox,self.basic_window_add_to_deck_dd,self.basic_window_put_text_button,self.basic_window_user_interface_increment_button,
        self.basic_window_user_interface_decrement_button,self.basic_window_voice_recorder_dd]

        self.scheduling_window_show_next_review_time_checkbox = CheckBox(self.SCHEDULING_WINDOW_NEXT_REVIEW_TIME_BB)
        self.scheduling_window_remaining_card_count_checkbox = CheckBox(self.SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB)
        self.scheduling_window_show_learning_cards_checkbox = CheckBox(self.SCHEDULING_WINDOW_SHOW_LEARNING_CARDS_BB)
        self.scheduling_window_legacy_timezone_checkbox = CheckBox(self.SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB)
        self.scheduling_window_v3_scheduler_checkbox = CheckBox(self.SCHEDULING_WINDOW_V3_SCHEDULER_BB)
        
        self.scheduling_window_next_day_increment_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB, self.increment_next_day)
        self.scheduling_window_learn_ahead_increment_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB, self.increment_learn_ahead)
        self.scheduling_window_timebox_time_increment_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB, self.increment_timebox_time)
        self.scheduling_window_next_day_decrement_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB, self.decrement_next_day)
        self.scheduling_window_learn_ahead_decrement_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB, self.decrement_learn_ahead)
        self.scheduling_window_timebox_time_decrement_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB, self.decrement_timebox_time)

        self.scheduling_window_widgets: List[Widget] = [self.scheduling_window_show_next_review_time_checkbox, self.scheduling_window_remaining_card_count_checkbox,
        self.scheduling_window_legacy_timezone_checkbox, self.scheduling_window_v3_scheduler_checkbox, self.scheduling_window_next_day_increment_button,
        self.scheduling_window_learn_ahead_increment_button, self.scheduling_window_timebox_time_increment_button, self.scheduling_window_next_day_decrement_button,
        self.scheduling_window_learn_ahead_decrement_button, self.scheduling_window_timebox_time_decrement_button, self.scheduling_window_show_learning_cards_checkbox]

        self.network_window_synchronize_audio_and_image_checkbox = CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB)
        self.network_window_synchronize_on_profile_checkbox = CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB)
        self.network_window_periodically_synchronize_checkbox = CheckBox(self.NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB)
        self.network_window_force_changes_in_one_direction_checkbox = CheckBox(self.NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB)

        self.network_window_widgets: List[Widget] = [self.network_window_synchronize_audio_and_image_checkbox, self.network_window_synchronize_on_profile_checkbox,
        self.network_window_periodically_synchronize_checkbox,self.network_window_force_changes_in_one_direction_checkbox]

        self.backups_window_increment_backups = Button(self.BACKUPS_WINDOW_INCREMENT_BB, self.increment_backup_number)
        self.backups_window_decrement_backups = Button(self.BACKUPS_WINDOW_DECREMENT_BB, self.decrement_backup_number)
        self.backups_window_widgets: List[Widget] = [self.backups_window_increment_backups, self.backups_window_decrement_backups]

        self.basic_window_dropdowns = [self.basic_window_language_dd,self.basic_window_add_to_deck_dd,self.basic_window_voice_recorder_dd,self.basic_window_video_driver_dd]

        self.dropdowns_to_str = {
            self.basic_window_language_dd: "basic_window_language_dd",
            self.basic_window_video_driver_dd: "basic_window_video_driver_dd",
            self.basic_window_add_to_deck_dd: "basic_window_add_to_deck_dd",
            self.basic_window_voice_recorder_dd: "basic_window_voice_recorder_dd",
        }

        self.checkboxes_to_str = {
            self.basic_window_show_play_buttons_checkbox : "basic_window_show_play_buttons_checkbox",
            self.basic_window_interrupt_audio_checkbox : "basic_window_interrupt_audio_checkbox",
            self.basic_window_paste_clipboard_images_checkbox : "basic_window_paste_clipboard_images_checkbox",
            self.basic_window_paste_without_shift_key_checkbox : "basic_window_paste_without_shift_key_checkbox",
            self.basic_window_night_mode_checkbox : "basic_window_night_mode_checkbox",
            self.scheduling_window_show_next_review_time_checkbox: "scheduling_window_show_next_review_time_checkbox",
            self.scheduling_window_remaining_card_count_checkbox: "scheduling_window_remaining_card_count_checkbox",
            self.scheduling_window_show_learning_cards_checkbox: "scheduling_window_show_learning_cards_checkbox",
            self.scheduling_window_legacy_timezone_checkbox: "scheduling_window_legacy_timezone_checkbox",
            self.scheduling_window_v3_scheduler_checkbox: "network_window_force_changes_in_one_direction_checkbox",
            self.network_window_synchronize_audio_and_image_checkbox: "network_window_synchronize_audio_and_image_checkbox",
            self.network_window_synchronize_on_profile_checkbox: "network_window_synchronize_on_profile_checkbox",
            self.network_window_periodically_synchronize_checkbox: "network_window_periodically_synchronize_checkbox",
            self.network_window_force_changes_in_one_direction_checkbox: "network_window_force_changes_in_one_direction_checkbox"
        }

        self.dropdowns_to_bbs = {
            self.basic_window_language_dd: self.BASIC_WINDOW_DD_1_BB,
            self.basic_window_video_driver_dd: self.BASIC_WINDOW_DD_2_BB,
            self.basic_window_add_to_deck_dd: self.BASIC_WINDOW_DD_3_BB,
            self.basic_window_voice_recorder_dd: self.BASIC_WINDOW_DD_4_BB,
        }

        self.set_reward_children([self.leads_to_external_website_popup])
    @property
    def reward_template(self):
        return {
            "window": ["open","close"],
            
            "help": 0,
            "basic_switch_button": 0,
            "scheduling_switch_button": 0,
            "network_switch_button": 0,
            "backup_switch_button": 0,

            "basic_window_show_play_buttons_checkbox" : [True,False],
            "basic_window_interrupt_audio_checkbox": [True,False],
            "basic_window_paste_clipboard_images_checkbox": [True,False],
            "basic_window_paste_without_shift_key_checkbox": [True,False],
            "basic_window_night_mode_checkbox": [True,False],
            
            "basic_window_language_dd" : {
                "opened": 0,
                "selected": [AnkiLanguages.ENGLISH.value, AnkiLanguages.GERMAN.value, AnkiLanguages.SPANISH.value]
            },
            "basic_window_video_driver_dd" : {
                "opened": 0,
                "selected": [VideoDriver.OPENGL.value, VideoDriver.ANGLE.value, VideoDriver.SOFTWARE.value]
            },
            "basic_window_add_to_deck_dd" : {
                "opened": 0,
                "selected": [DeckAddType.ADD_TO_CURRENT.value, DeckAddType.CHANGE_DECK.value]
            },
            "basic_window_voice_recorder_dd" : {
                "opened": 0,
                "selected": [VoiceRecorder.QT.value, VoiceRecorder.PY_AUDIO.value]
            },

            "basic_window_user_interface_increment_button": 0,
            "basic_window_user_interface_decrement_button": 0,
            "basic_window_put_text_button": 0,

            "scheduling_window_show_next_review_time_checkbox": [True,False],
            "scheduling_window_remaining_card_count_checkbox": [True,False],
            "scheduling_window_show_learning_cards_checkbox": [True,False],
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

            "backups_window_increment_backups": 0,
            "backups_window_decrement_backups": 0
        }
        
    def set_basic(self):
        for i in range (1,5):
            self.get_state()[i] = 0
        self.get_state()[1] = 1
    
    def set_scheduling(self):
        for i in range (1,5):
            self.get_state()[i] = 0
        self.get_state()[2] = 1
    
    def set_network(self):
        for i in range (1,5):
            self.get_state()[i] = 0
        self.get_state()[3] = 1
    
    def set_backup(self):
        for i in range (1,5):
            self.get_state()[i] = 0
        self.get_state()[4] = 1
    
    def increment_backup_number(self):
        if (self.backup_number < 100):
            self.backup_number += 1
            self.register_selected_reward(["backups_window_increment_backups"])

    def decrement_backup_number(self):
        if (self.backup_number > 0):
            self.backup_number -= 1
            self.register_selected_reward(["backups_window_decrement_backups"])

    def handle_click(self,click_position: np.ndarray):
        if(self.leads_to_external_website_popup.is_open()):
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if (self.basic_switch_button.is_clicked_by(click_position)):
            self.basic_switch_button.handle_click(click_position)
            self.register_selected_reward(["basic_switch_button"])
        elif (self.scheduling_switch_button.is_clicked_by(click_position)):
            self.scheduling_switch_button.handle_click(click_position)
            self.register_selected_reward(["scheduling_switch_button"])
        elif (self.network_switch_button.is_clicked_by(click_position)):
            self.network_switch_button.handle_click(click_position)
            self.register_selected_reward(["network_switch_button"])
        elif (self.backup_switch_button.is_clicked_by(click_position)):
            self.backup_switch_button.handle_click(click_position)
            self.register_selected_reward(["backup_switch_button"])
        elif(self.close_button.is_clicked_by(click_position)):
            self.close_button.handle_click(click_position)
        elif(self.help_button.is_clicked_by(click_position)):
            self.help_button.handle_click(click_position)
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
        if self.open_dd is not None:
            self.open_dd.handle_click(click_position)
            self.open_dd = None
            return
            
        for dd in self.basic_window_dropdowns:
            if self.dropdowns_to_bbs[dd].is_point_inside(click_position):
                self.open_dd = dd
                self.close_all_dropdowns()
                self.open_dd.open()
                return

        for widget in self.basic_window_widgets:
            if (widget.is_clicked_by(click_position) and not(isinstance(widget, Dropdown))):
                    widget.handle_click(click_position)
                    
    def handle_click_scheduling_window(self,click_position: np.ndarray):
        for widget in self.scheduling_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
                if isinstance(widget, CheckBox):
                    self.register_selected_reward([self.checkboxes_to_str[widget],widget.get_state()[0]])
    
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
        self.current_search_text = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self.register_selected_reward(["basic_window_put_text_button"])

    def help(self):
        self.leads_to_external_website_popup.open()
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
        if (self.get_state()[1] == 1):
            to_render = cv2.imread(self.PREFERENCES_BASIC_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            put_text(img, f"{self.user_interface}", (163, 522), font_scale = 0.4)
            put_text(img, "" if self.current_search_text is None else f"{self.current_search_text}" , (43, 481), font_scale = 0.4)
            for widget in self.basic_window_widgets:
                if isinstance(widget,CheckBox):
                    img = widget.render(img)
            for dd in self.basic_window_dropdowns:
                if dd.get_selected_item() is not None:
                    put_text(img, dd.get_selected_item().display_name, (self.dropdowns_to_bbs[dd].x + 10,(self.dropdowns_to_bbs[dd].y + 18) ),font_scale=0.5)
            if self.open_dd is not None:
                img = self.open_dd.render(img)
        elif (self.get_state()[2] == 1):
            to_render = cv2.imread(self.PREFERENCES_SCHEDULING_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            for widget in self.scheduling_window_widgets:
                if isinstance(widget,CheckBox):
                    img = widget.render(img)
            put_text(img, f"{self.next_day}" , (379, 281), font_scale = 0.4)
            put_text(img, f"{self.learn_ahead}" , (379, 317), font_scale = 0.4)
            put_text(img, f"{self.timebox_time}" , (379, 355), font_scale = 0.4)
        elif (self.get_state()[3] == 1):
            to_render = cv2.imread(self.PREFERENCES_NETWORK_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            for widget in self.network_window_widgets:
                if isinstance(widget,CheckBox):
                    img = widget.render(img)
        elif (self.get_state()[4] == 1):
            to_render = cv2.imread(self.PREFERENCES_BACKUP_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            put_text(img, f"{self.backup_number}" , (93, 161), font_scale = 0.4)
        if(self.leads_to_external_website_popup.is_open()):
            img = self.leads_to_external_website_popup.render(img)
        return img

    def close_all_dropdowns(self):
        for dd in self.basic_window_dropdowns:
            dd.close()