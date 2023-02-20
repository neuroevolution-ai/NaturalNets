import os
import random
import string
from typing import List
import cv2
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH, AnkiLanguages, DeckAddType, VideoDriver, VoiceRecorder
from naturalnets.environments.anki.pages.main_page_popups.leads_to_external_website_popup \
    import LeadsToExternalWebsitePopup
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page, Widget
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.utils import render_onto_bb, put_text
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.check_box import CheckBox
from naturalnets.environments.gui_app.widgets.dropdown import Dropdown, DropdownItem

class PreferencesPage(RewardElement, Page):
    """
    Actually the whole page is a filler and an imitation of the original application and does not
    affect the logic
    State description:
            state[0]: if this window is open
            state[j]: i-th tab is open j = {1,2,3,4}
    """

    WINDOW_BB = BoundingBox(20, 80, 801, 601)
    STATE_LEN = 5

    PREFERENCES_BASIC_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_basic_page.png")
    PREFERENCES_SCHEDULING_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_scheduling_page.png")
    PREFERENCES_NETWORK_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_network_page.png")
    PREFERENCES_BACKUP_IMG_PATH = os.path.join(IMAGES_PATH, "preferences_backup_page.png")

    CLOSE_BB = BoundingBox(545, 640, 98, 26)
    HELP_BB = BoundingBox(683, 640, 98, 26)

    BASIC_SWITCH_BB = BoundingBox(62, 117, 145, 41)
    SCHEDULING_SWITCH_BB = BoundingBox(209, 117, 145, 41)
    NETWORK_SWITCH_BB = BoundingBox(355, 117, 145, 41)
    BACKUP_SWITCH_BB = BoundingBox(501, 117, 145, 41)

    BASIC_WINDOW_DD_1_BB = BoundingBox(90, 176, 644, 29)
    BASIC_WINDOW_DD_2_BB = BoundingBox(90, 225, 644, 29)
    BASIC_WINDOW_DD_3_BB = BoundingBox(90, 412, 644, 29)
    BASIC_WINDOW_DD_4_BB = BoundingBox(90, 462, 644, 29)

    BASIC_WINDOW_DD_1_BB_OFFSET = BoundingBox(90, 205, 644, 29)
    BASIC_WINDOW_DD_2_BB_OFFSET = BoundingBox(90, 254, 644, 29)
    BASIC_WINDOW_DD_3_BB_OFFSET = BoundingBox(90, 441, 644, 29)
    BASIC_WINDOW_DD_4_BB_OFFSET = BoundingBox(90, 491, 644, 29)

    BASIC_WINDOW_1_CHECKBOX_BB = BoundingBox(90, 276, 16, 16)
    BASIC_WINDOW_2_CHECKBOX_BB = BoundingBox(90, 303, 16, 16)
    BASIC_WINDOW_3_CHECKBOX_BB = BoundingBox(90, 330, 16, 16)
    BASIC_WINDOW_4_CHECKBOX_BB = BoundingBox(90, 357, 16, 16)
    BASIC_WINDOW_5_CHECKBOX_BB = BoundingBox(90, 383, 16, 16)

    BASIC_WINDOW_SEARCH_TEXT_BB = BoundingBox(653, 524, 94, 31)
    BASIC_WINDOW_USER_INTERFACE_INCREMENT = BoundingBox(317, 576, 13, 9)
    BASIC_WINDOW_USER_INTERFACE_DECREMENT = BoundingBox(317, 585, 13, 9)

    SCHEDULING_WINDOW_NEXT_REVIEW_TIME_BB = BoundingBox(81, 181, 16, 16)
    SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB = BoundingBox(81, 223, 16, 16)
    SCHEDULING_WINDOW_SHOW_LEARNING_CARDS_BB = BoundingBox(81, 269, 16, 16)
    SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB = BoundingBox(81, 319, 16, 16)
    SCHEDULING_WINDOW_V3_SCHEDULER_BB = BoundingBox(81, 360, 16, 16)

    SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB = BoundingBox(415, 414, 12, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB = BoundingBox(415, 455, 12, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB = BoundingBox(415, 496, 18, 9)

    SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB = BoundingBox(415, 426, 12, 9)
    SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB = BoundingBox(415, 464, 12, 9)
    SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB = BoundingBox(415, 505, 12, 9)

    NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB = BoundingBox(75, 241, 16, 16)
    NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB = BoundingBox(75, 284, 16, 16)
    NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB = BoundingBox(75, 327, 16, 16)
    NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB = BoundingBox(75, 368, 16, 16)

    BACKUPS_WINDOW_INCREMENT_BB = BoundingBox(294, 195, 12, 9)
    BACKUPS_WINDOW_DECREMENT_BB = BoundingBox(295, 205, 12, 9)
    USER_INTERFACE_X = 283
    USER_INTERFACE_Y = 590
    CURRENT_SEARCH_TEXT_X = 97
    CURRENT_SEARCH_TEXT_Y = 544
    NEXT_DAY_X = 381
    NEXT_DAY_Y = 427
    LEARN_AHEAD_X = 381
    LEARN_AHEAD_Y = 468
    TIMEBOX_TIME_X = 381
    TIMEBOX_TIME_Y = 510
    BACKUP_NUMBER_X = 255
    BACKUP_NUMBER_Y = 208
    
    """
       Singleton design pattern to ensure that at most one
       PreferencesPage is present
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PreferencesPage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        Page.__init__(self, self.STATE_LEN, self.WINDOW_BB, self.PREFERENCES_BASIC_IMG_PATH)
        RewardElement.__init__(self)
        self.get_state()[1] = 1
        # Appears when the help button is clicked
        self.leads_to_external_website_popup = LeadsToExternalWebsitePopup()
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

        self.basic_window_add_to_current_ddi = DropdownItem(DeckAddType.ADD_TO_CURRENT,
                                                            DeckAddType.ADD_TO_CURRENT.value)
        self.basic_window_change_deck_ddi = DropdownItem(DeckAddType.CHANGE_DECK, DeckAddType.CHANGE_DECK.value)

        self.basic_window_voice_recorder_qt_ddi = DropdownItem(VoiceRecorder.PY_AUDIO, VoiceRecorder.PY_AUDIO.value)
        self.basic_window_voice_recorder_py_audio_ddi = DropdownItem(VoiceRecorder.QT, VoiceRecorder.QT.value)

        self.basic_window_language_dd = Dropdown(self.BASIC_WINDOW_DD_1_BB_OFFSET,
                                                 [self.basic_window_english_ddi, self.basic_window_german_ddi,
                                                  self.basic_window_spanish_ddi])
        self.basic_window_video_driver_dd = Dropdown(self.BASIC_WINDOW_DD_2_BB_OFFSET,
                                                     [self.basic_window_video_driver_opengl_ddi,
                                                      self.basic_window_video_driver_angle_ddi,
                                                      self.basic_window_video_driver_software_ddi])
        self.basic_window_add_to_deck_dd = Dropdown(self.BASIC_WINDOW_DD_3_BB_OFFSET,
                                                    [self.basic_window_add_to_current_ddi,
                                                     self.basic_window_change_deck_ddi])
        self.basic_window_voice_recorder_dd = Dropdown(self.BASIC_WINDOW_DD_4_BB_OFFSET,
                                                       [self.basic_window_voice_recorder_qt_ddi,
                                                        self.basic_window_voice_recorder_py_audio_ddi])

        self.basic_window_show_play_buttons_checkbox = CheckBox(self.BASIC_WINDOW_1_CHECKBOX_BB)
        self.basic_window_interrupt_audio_checkbox = CheckBox(self.BASIC_WINDOW_2_CHECKBOX_BB)
        self.basic_window_paste_clipboard_images_checkbox = CheckBox(self.BASIC_WINDOW_3_CHECKBOX_BB)
        self.basic_window_paste_without_shift_key_checkbox = CheckBox(self.BASIC_WINDOW_4_CHECKBOX_BB)
        self.basic_window_night_mode_checkbox = CheckBox(self.BASIC_WINDOW_5_CHECKBOX_BB)

        self.basic_window_put_text_button = Button(self.BASIC_WINDOW_SEARCH_TEXT_BB, self.set_current_search_text)
        self.basic_window_user_interface_increment_button = Button(self.BASIC_WINDOW_USER_INTERFACE_INCREMENT,
                                                                   self.increment_user_interface)
        self.basic_window_user_interface_decrement_button = Button(self.BASIC_WINDOW_USER_INTERFACE_DECREMENT,
                                                                   self.decrement_user_interface)

        self.basic_window_widgets: List[Widget] = [self.basic_window_language_dd, self.basic_window_video_driver_dd,
                                                   self.basic_window_show_play_buttons_checkbox,
                                                   self.basic_window_interrupt_audio_checkbox,
                                                   self.basic_window_paste_clipboard_images_checkbox,
                                                   self.basic_window_paste_without_shift_key_checkbox,
                                                   self.basic_window_night_mode_checkbox,
                                                   self.basic_window_add_to_deck_dd, self.basic_window_put_text_button,
                                                   self.basic_window_user_interface_increment_button,
                                                   self.basic_window_user_interface_decrement_button,
                                                   self.basic_window_voice_recorder_dd]

        self.scheduling_window_show_next_review_time_checkbox = CheckBox(self.SCHEDULING_WINDOW_NEXT_REVIEW_TIME_BB)
        self.scheduling_window_remaining_card_count_checkbox = CheckBox(self.SCHEDULING_WINDOW_REMAINING_CARD_COUNT_BB)
        self.scheduling_window_show_learning_cards_checkbox = CheckBox(self.SCHEDULING_WINDOW_SHOW_LEARNING_CARDS_BB)
        self.scheduling_window_legacy_timezone_checkbox = CheckBox(self.SCHEDULING_WINDOW_LEGACY_TIMEZONE_BB)
        self.scheduling_window_v3_scheduler_checkbox = CheckBox(self.SCHEDULING_WINDOW_V3_SCHEDULER_BB)

        self.scheduling_window_next_day_increment_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_INCREMENT_BB,
                                                                  self.increment_next_day)
        self.scheduling_window_learn_ahead_increment_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_INCREMENT_BB,
                                                                     self.increment_learn_ahead)
        self.scheduling_window_timebox_time_increment_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_INCREMENT_BB,
                                                                      self.increment_timebox_time)
        self.scheduling_window_next_day_decrement_button = Button(self.SCHEDULING_WINDOW_NEXT_DAY_DECREMENT_BB,
                                                                  self.decrement_next_day)
        self.scheduling_window_learn_ahead_decrement_button = Button(self.SCHEDULING_WINDOW_LEARN_AHEAD_DECREMENT_BB,
                                                                     self.decrement_learn_ahead)
        self.scheduling_window_timebox_time_decrement_button = Button(self.SCHEDULING_WINDOW_TIMEBOX_TIME_DECREMENT_BB,
                                                                      self.decrement_timebox_time)

        self.scheduling_window_widgets: List[Widget] = [self.scheduling_window_show_next_review_time_checkbox,
                                                        self.scheduling_window_remaining_card_count_checkbox,
                                                        self.scheduling_window_legacy_timezone_checkbox,
                                                        self.scheduling_window_v3_scheduler_checkbox,
                                                        self.scheduling_window_next_day_increment_button,
                                                        self.scheduling_window_learn_ahead_increment_button,
                                                        self.scheduling_window_timebox_time_increment_button,
                                                        self.scheduling_window_next_day_decrement_button,
                                                        self.scheduling_window_learn_ahead_decrement_button,
                                                        self.scheduling_window_timebox_time_decrement_button,
                                                        self.scheduling_window_show_learning_cards_checkbox]

        self.network_window_synchronize_audio_and_image_checkbox = \
            CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_AUDIO_AND_IMAGE_BB)
        self.network_window_synchronize_on_profile_checkbox = \
            CheckBox(self.NETWORK_WINDOW_SYNCHRONIZE_ON_PROFILE_BB)
        self.network_window_periodically_synchronize_checkbox = \
            CheckBox(self.NETWORK_WINDOW_PERIODICALLY_SYNCHRONIZE_BB)
        self.network_window_force_changes_in_one_direction_checkbox = \
            CheckBox(self.NETWORK_WINDOW_FORCE_CHANGES_IN_ONE_DIRECTION_BB)

        self.network_window_widgets: List[Widget] = [self.network_window_synchronize_audio_and_image_checkbox,
                                                     self.network_window_synchronize_on_profile_checkbox,
                                                     self.network_window_periodically_synchronize_checkbox,
                                                     self.network_window_force_changes_in_one_direction_checkbox]

        self.backups_window_increment_backups = Button(self.BACKUPS_WINDOW_INCREMENT_BB, self.increment_backup_number)
        self.backups_window_decrement_backups = Button(self.BACKUPS_WINDOW_DECREMENT_BB, self.decrement_backup_number)
        self.backups_window_widgets: List[Button] = [self.backups_window_increment_backups,
                                                     self.backups_window_decrement_backups]

        self.basic_window_dropdowns = [self.basic_window_language_dd, self.basic_window_add_to_deck_dd,
                                       self.basic_window_voice_recorder_dd, self.basic_window_video_driver_dd]

        self.dropdowns_to_str = {
            self.basic_window_language_dd:
                "basic_window_language_dd",
            self.basic_window_video_driver_dd:
                "basic_window_video_driver_dd",
            self.basic_window_add_to_deck_dd:
                "basic_window_add_to_deck_dd",
            self.basic_window_voice_recorder_dd:
                "basic_window_voice_recorder_dd",
        }

        self.checkboxes_to_str = {
            self.basic_window_show_play_buttons_checkbox:
                "basic_window_show_play_buttons_checkbox",
            self.basic_window_interrupt_audio_checkbox:
                "basic_window_interrupt_audio_checkbox",
            self.basic_window_paste_clipboard_images_checkbox:
                "basic_window_paste_clipboard_images_checkbox",
            self.basic_window_paste_without_shift_key_checkbox:
                "basic_window_paste_without_shift_key_checkbox",
            self.basic_window_night_mode_checkbox:
                "basic_window_night_mode_checkbox",
            self.scheduling_window_show_next_review_time_checkbox:
                "scheduling_window_show_next_review_time_checkbox",
            self.scheduling_window_remaining_card_count_checkbox:
                "scheduling_window_remaining_card_count_checkbox",
            self.scheduling_window_show_learning_cards_checkbox:
                "scheduling_window_show_learning_cards_checkbox",
            self.scheduling_window_legacy_timezone_checkbox:
                "scheduling_window_legacy_timezone_checkbox",
            self.scheduling_window_v3_scheduler_checkbox:
                "scheduling_window_v3_scheduler_checkbox",
            self.network_window_synchronize_audio_and_image_checkbox:
                "network_window_synchronize_audio_and_image_checkbox",
            self.network_window_synchronize_on_profile_checkbox:
                "network_window_synchronize_on_profile_checkbox",
            self.network_window_periodically_synchronize_checkbox:
                "network_window_periodically_synchronize_checkbox",
            self.network_window_force_changes_in_one_direction_checkbox:
                "network_window_force_changes_in_one_direction_checkbox"
        }

        self.dropdowns_to_bbs = {
            self.basic_window_language_dd: self.BASIC_WINDOW_DD_1_BB,
            self.basic_window_video_driver_dd: self.BASIC_WINDOW_DD_2_BB,
            self.basic_window_add_to_deck_dd: self.BASIC_WINDOW_DD_3_BB,
            self.basic_window_voice_recorder_dd: self.BASIC_WINDOW_DD_4_BB,
        }
        self.add_child(self.leads_to_external_website_popup)
        self.set_reward_children([self.leads_to_external_website_popup])

    """
    Provide rewards for opening/closing this page and selecting dropdown items and checkboxes etc.
    """
    @property
    def reward_template(self):
        return {
            "window": ["open", "close"],

            "help": 0,
            "basic_switch_button": 0,
            "scheduling_switch_button": 0,
            "network_switch_button": 0,
            "backup_switch_button": 0,

            "basic_window_show_play_buttons_checkbox": [True, False],
            "basic_window_interrupt_audio_checkbox": [True, False],
            "basic_window_paste_clipboard_images_checkbox": [True, False],
            "basic_window_paste_without_shift_key_checkbox": [True, False],
            "basic_window_night_mode_checkbox": [True, False],

            "basic_window_language_dd": {
                "opened": 0,
                "selected": [AnkiLanguages.ENGLISH.value, AnkiLanguages.GERMAN.value, AnkiLanguages.SPANISH.value]
            },
            "basic_window_video_driver_dd": {
                "opened": 0,
                "selected": [VideoDriver.OPENGL.value, VideoDriver.ANGLE.value, VideoDriver.SOFTWARE.value]
            },
            "basic_window_add_to_deck_dd": {
                "opened": 0,
                "selected": [DeckAddType.ADD_TO_CURRENT.value, DeckAddType.CHANGE_DECK.value]
            },
            "basic_window_voice_recorder_dd": {
                "opened": 0,
                "selected": [VoiceRecorder.QT.value, VoiceRecorder.PY_AUDIO.value]
            },

            "basic_window_user_interface_increment_button": 0,
            "basic_window_user_interface_decrement_button": 0,
            "basic_window_put_text_button": 0,

            "scheduling_window_show_next_review_time_checkbox": [True, False],
            "scheduling_window_remaining_card_count_checkbox": [True, False],
            "scheduling_window_show_learning_cards_checkbox": [True, False],
            "scheduling_window_legacy_timezone_checkbox": [True, False],
            "scheduling_window_v3_scheduler_checkbox": [True, False],

            "scheduling_window_next_day_increment_button": 0,
            "scheduling_window_learn_ahead_increment_button": 0,
            "scheduling_window_timebox_time_increment_button": 0,
            "scheduling_window_next_day_decrement_button": 0,
            "scheduling_window_learn_ahead_decrement_button": 0,
            "scheduling_window_timebox_time_decrement_button": 0,

            "network_window_synchronize_audio_and_image_checkbox": [True, False],
            "network_window_synchronize_on_profile_checkbox": [True, False],
            "network_window_periodically_synchronize_checkbox": [True, False],
            "network_window_force_changes_in_one_direction_checkbox": [True, False],

            "backups_window_increment_backups": 0,
            "backups_window_decrement_backups": 0
        }

    """
    Set the current tab to basic
    """
    def set_basic(self):
        self.get_state()[1:5] = 0
        self.get_state()[1] = 1

    """
    Set the current tab to scheduling
    """
    def set_scheduling(self):
        self.get_state()[1:5] = 0
        self.get_state()[2] = 1

    """
    Set the current tab to network
    """
    def set_network(self):
        self.get_state()[1:5] = 0
        self.get_state()[3] = 1

    """
    Set the current tab to backup
    """
    def set_backup(self):
        self.get_state()[1:5] = 0
        self.get_state()[4] = 1
    """
    Increment the backup number and provide the reward of it
    """
    def increment_backup_number(self):
        if self.backup_number < 100:
            self.backup_number += 1
            self.register_selected_reward(["backups_window_increment_backups"])

    """
    Decrement the backup number and provide the reward of it
    """
    def decrement_backup_number(self):
        if self.backup_number > 0:
            self.backup_number -= 1
            self.register_selected_reward(["backups_window_decrement_backups"])

    """
    Delegate the click to the popup if it is open 
    else check if a bounding box for switching tab is selected and then switch the tab
    else check close or help button is clicked and handle click
    else delegate click to methods for handling click by open tab 
    """
    def handle_click(self, click_position: np.ndarray):
        if self.leads_to_external_website_popup.is_open():
            self.leads_to_external_website_popup.handle_click(click_position)
            return
        if self.basic_switch_button.is_clicked_by(click_position):
            self.basic_switch_button.handle_click(click_position)
            self.register_selected_reward(["basic_switch_button"])
        elif self.scheduling_switch_button.is_clicked_by(click_position):
            self.scheduling_switch_button.handle_click(click_position)
            self.register_selected_reward(["scheduling_switch_button"])
        elif self.network_switch_button.is_clicked_by(click_position):
            self.network_switch_button.handle_click(click_position)
            self.register_selected_reward(["network_switch_button"])
        elif self.backup_switch_button.is_clicked_by(click_position):
            self.backup_switch_button.handle_click(click_position)
            self.register_selected_reward(["backup_switch_button"])
        elif self.close_button.is_clicked_by(click_position):
            self.close_button.handle_click(click_position)
        elif self.help_button.is_clicked_by(click_position):
            self.help_button.handle_click(click_position)
        else:
            self.handle_click_by_open_window(click_position)
    """
    Delegate the click to the open tab
    """
    def handle_click_by_open_window(self, click_position: np.ndarray):
        if self.get_state()[1] == 1:
            self.handle_click_basic_window(click_position)
        elif self.get_state()[2] == 1:
            self.handle_click_scheduling_window(click_position)
        elif self.get_state()[3] == 1:
            self.handle_click_network_window(click_position)
        elif self.get_state()[4] == 1:
            self.handle_click_backups_window(click_position)
    """
    if a dropdown is open then delegates the click to it
    else if a dropdown bounding box is clicked then opens the dropdown
    else handles the click by widgets
    """
    def handle_click_basic_window(self, click_position: np.ndarray):
        if self.open_dd is not None:
            self.open_dd.handle_click(click_position)
            if self.open_dd.get_selected_item() is not None:
                self.register_selected_reward([self.dropdowns_to_str[self.open_dd], "selected",
                                               self.open_dd.get_selected_item().get_value().value])
            self.open_dd = None
            return

        for dd in self.basic_window_dropdowns:
            if self.dropdowns_to_bbs[dd].is_point_inside(click_position):
                self.open_dd = dd
                self.register_selected_reward([self.dropdowns_to_str[self.open_dd], "opened"])
                self.close_all_dropdowns()
                self.open_dd.open()
                return

        for widget in self.basic_window_widgets:
            if widget.is_clicked_by(click_position) and not (isinstance(widget, Dropdown)):
                widget.handle_click(click_position)
                if isinstance(widget, CheckBox):
                    self.register_selected_reward([self.checkboxes_to_str[widget], not (widget.is_selected())])
    """
    Execute click action if a widget from scheduling window is clicked
    """
    def handle_click_scheduling_window(self, click_position: np.ndarray):
        for widget in self.scheduling_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
                if isinstance(widget, CheckBox):
                    self.register_selected_reward([self.checkboxes_to_str[widget], not (widget.is_selected())])

    """
    Execute click action if a widget from network tab is clicked
    """
    def handle_click_network_window(self, click_position: np.ndarray):
        for widget in self.network_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
                if isinstance(widget, CheckBox):
                    self.register_selected_reward([self.checkboxes_to_str[widget], not (widget.is_selected())])

    """
    Execute click action if a widget from backups tab is clicked
    """
    def handle_click_backups_window(self, click_position: np.ndarray):
        for widget in self.backups_window_widgets:
            if widget.is_clicked_by(click_position):
                widget.handle_click(click_position)
    """
    Increment the user interface attribute from the basic tab and provide reward of it
    """
    def increment_user_interface(self):
        if self.user_interface < 200:
            self.user_interface += 5
            self.register_selected_reward(["basic_window_user_interface_increment_button"])

    """
    Decrement the user interface attribute from the basic tab and provide reward of it
    """
    def decrement_user_interface(self):
        if self.user_interface > 50:
            self.user_interface -= 5
            self.register_selected_reward(["basic_window_user_interface_decrement_button"])

    """
    Increment the next day attribute from the scheduling tab and provide reward of it
    """
    def increment_next_day(self):
        if self.next_day < 10:
            self.next_day += 1
            self.register_selected_reward(["scheduling_window_next_day_increment_button"])

    """
    Decrement the next day attribute from the scheduling tab and provide reward of it
    """
    def decrement_next_day(self):
        if self.next_day > 0:
            self.next_day -= 1
            self.register_selected_reward(["scheduling_window_next_day_decrement_button"])

    """
    Increment the learn ahead attribute from the scheduling tab and provide reward of it
    """
    def increment_learn_ahead(self):
        if self.learn_ahead < 40:
            self.learn_ahead += 1
            self.register_selected_reward(["scheduling_window_learn_ahead_increment_button"])

    """
    Decrement the learn ahead attribute from the scheduling tab and provide reward of it
    """
    def decrement_learn_ahead(self):
        if self.learn_ahead > 0:
            self.learn_ahead -= 1
            self.register_selected_reward(["scheduling_window_learn_ahead_decrement_button"])
    """
    Increment the timebox time attribute from the scheduling tab and provide reward of it
    """
    def increment_timebox_time(self):
        if self.timebox_time < 20:
            self.timebox_time += 1
            self.register_selected_reward(["scheduling_window_timebox_time_increment_button"])

    """
    Decrement the timebox time attribute from the scheduling tab and provide reward of it
    """
    def decrement_timebox_time(self):
        if self.timebox_time > 0:
            self.timebox_time -= 1
            self.register_selected_reward(["scheduling_window_timebox_time_decrement_button"])

    """
    Set the current search text attribute of the basic window and provide the reward of it
    """
    def set_current_search_text(self):
        self.current_search_text = 'Cool search name'
        self.register_selected_reward(["basic_window_put_text_button"])
    
    """
    Click action of help button
    """
    def help(self):
        self.leads_to_external_website_popup.open()
        self.register_selected_reward(["help"])
    
    """
    Opens this window
    """
    def open(self):
        self.get_state()[0] = 1
        self.register_selected_reward(["window", "open"])

    """
    Closes this window
    """
    def close(self):
        self.get_state()[0] = 0
        self.register_selected_reward(["window", "close"])
    """
    Returns true if this window is open
    """
    def is_open(self):
        return self.get_state()[0]
    """
    Render the image of this page according to the open window and 
    if the popup is open then it is going to be rendered too
    """
    def render(self, img: np.ndarray):
        if self.get_state()[1] == 1:
            to_render = cv2.imread(self.PREFERENCES_BASIC_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            put_text(img, f"{self.user_interface}", (self.USER_INTERFACE_X,self.USER_INTERFACE_Y), font_scale=0.4)
            put_text(img, "" if self.current_search_text is None else f"{self.current_search_text}", (self.CURRENT_SEARCH_TEXT_X, self.CURRENT_SEARCH_TEXT_Y),
                     font_scale=0.4)
            for widget in self.basic_window_widgets:
                if isinstance(widget, CheckBox):
                    img = widget.render(img)
            for dd in self.basic_window_dropdowns:
                if dd.get_selected_item() is not None:
                    put_text(img, dd.get_selected_item().display_name,
                             (self.dropdowns_to_bbs[dd].x + 10, (self.dropdowns_to_bbs[dd].y + 19)), font_scale=0.4)
            if self.open_dd is not None:
                img = self.open_dd.render(img)
        elif self.get_state()[2] == 1:
            to_render = cv2.imread(self.PREFERENCES_SCHEDULING_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            for widget in self.scheduling_window_widgets:
                if isinstance(widget, CheckBox):
                    img = widget.render(img)
            put_text(img, f"{self.next_day}", (self.NEXT_DAY_X, self.NEXT_DAY_Y), font_scale=0.4)
            put_text(img, f"{self.learn_ahead}", (self.LEARN_AHEAD_X, self.LEARN_AHEAD_Y), font_scale=0.4)
            put_text(img, f"{self.timebox_time}", (self.TIMEBOX_TIME_X, self.TIMEBOX_TIME_Y), font_scale=0.4)
        elif self.get_state()[3] == 1:
            to_render = cv2.imread(self.PREFERENCES_NETWORK_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            for widget in self.network_window_widgets:
                if isinstance(widget, CheckBox):
                    img = widget.render(img)
        elif self.get_state()[4] == 1:
            to_render = cv2.imread(self.PREFERENCES_BACKUP_IMG_PATH)
            img = render_onto_bb(img, self.get_bb(), to_render)
            put_text(img, f"{self.backup_number}", (self.BACKUP_NUMBER_X, self.BACKUP_NUMBER_Y), font_scale=0.4)
        if self.leads_to_external_website_popup.is_open():
            img = self.leads_to_external_website_popup.render(img)
        return img
    """
    Method to close all of the dropdowns of the basic tab
    """
    def close_all_dropdowns(self):
        for dd in self.basic_window_dropdowns:
            dd.close()

    def reset(self):
        self.current_search_text = None
        self.user_interface = 100
        self.next_day = 4
        self.learn_ahead = 20
        self.timebox_time = 5
        self.backup_number = 50
        for widget in self.basic_window_widgets:
            if(isinstance(widget,CheckBox)):
                widget.get_state()[0] = 0
            elif(isinstance(widget,Dropdown)):
                widget._selected_item = None
        for widget in self.scheduling_window_widgets:
            widget.get_state()[0] = 0
        for widget in self.network_window_widgets:
            widget.get_state()[0] = 0
        