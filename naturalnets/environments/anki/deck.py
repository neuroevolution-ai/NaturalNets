from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.constants import InsertionOrder
from naturalnets.environments.anki.constants import LeechAction
from naturalnets.environments.anki.deck import Deck
from naturalnets.environments.anki.deck import DeckOption
import numpy as np
from naturalnets.environments.anki.constants import StandardSettingValues

class Deck():
    
    def __init__(self):
        self.cards: list[Card] = []
        self.current_option: DeckOption = DeckOption("Default",True)

    def add_card(self,card: Card):
        if self.cards.count(card) != 0:
            self.cards.append(card)
    
    def remove_card(self,card: Card):
        self.cards.remove(card)

class DeckOption():

    def __init__(self, name: str, is_default_option: bool):
        self.name: str = name
        self.card_number: int = StandardSettingValues.NEW_CARDS_PER_DAY
        self.max_review_number: int = StandardSettingValues.MAX_REVIEWS_PER_DAY
        self.again_duration_minutes: int = StandardSettingValues.AGAIN_LEARNING_STEP_MIN
        self.good_duration_minutes: int = StandardSettingValues.GOOD_LEARNING_STEP_MIN
        self.graduating_duration_days: int = StandardSettingValues.GRADUATING_INTERVAL_STEP_DAY
        self.easy_duration_days: int = StandardSettingValues.EASY_INTERVAL_STEP_DAY
        self.insertion_order: InsertionOrder = InsertionOrder.SEQUENTIAL
        self.relearning_steps_minutes: int = StandardSettingValues.RELEARNING_STEPS_MIN
        self.minumum_interval: int = StandardSettingValues.MIN_INTERVAL
        self.leech_threshold: int = StandardSettingValues.LEECH_THRESHOLD
        self.leech_action: LeechAction = LeechAction.TAG_ONLY
        self.maximum_answer_seconds: int = StandardSettingValues.MAX_ANSWER_SECONDS
        self.is_answer_time_shown: bool = StandardSettingValues.SHOW_ANSWER_TIME
        self.is_new_siblings_buried: bool = StandardSettingValues.BURY_NEW_SIBLINGS
        self.is_review_siblings_buried: bool = StandardSettingValues.BURY_REVIEW_SIBLINGS
        self.is_audio_automatically_replayed: bool = StandardSettingValues.PLAY_AUDIO_AUTOMATICALLY
        self.is_question_skipped: bool = StandardSettingValues.SKIP_QUESTION_WHEN_REPLAYING_ANSWER
        self.maximum_interval_days: int = StandardSettingValues.MAX_INTERVAL_DAYS
        self.starting_ease: float = StandardSettingValues.STARTING_EASE
        self.easy_bonus: float = StandardSettingValues.EASY_BONUS
        self.interval_modifier: float = StandardSettingValues.INTERVAL_MODIFIER
        self.hard_interval: float = StandardSettingValues.HARD_INTERVAL
        self.new_interval: float = StandardSettingValues.NEW_INTERVAL
        self.is_default_option: bool = is_default_option

    def increment_card_number(self):
        self.card_number += 1
        if 10 * self.card_number > self.max_review_number:
            self.max_review_number = 10 * self.card_number

    def decrement_card_number(self):
        if self.card_number - 1 <= 0:
            pass
        else :
            self.card_number -= 1
    
    def increment_max_review_number(self):
        self.max_review_number += 1

    def decrement_max_review_number(self):
        self.max_review_number -= 1
        if 10 * self.card_number > self.max_review_number:
            self.max_review_number = 10 * self.card_number
    
    def increment_again_duration_minutes(self):
        if self.again_duration_minutes + 1 > self.good_duration_minutes:
            pass
        else :
            self.again_duration_minutes += 1
    
    def decrement_again_duration_minutes(self):
        if self.again_duration_minutes < 1:
            pass
        else :
            self.again_duration_minutes -= 1
    
    def increment_good_duration_minutes(self):
        if self.good_duration_minutes + 1 > 1440 * self.graduating_duration_days:
            pass
        else :
            self.good_duration_minutes += 1
    
    def decrement_good_duration_minutes(self):
        if self.good_duration_minutes - 1 < self.again_duration_minutes:
            pass
        else:
            self.good_duration_minutes -= 1

    def increment_graduating_duration_days(self):
        if self.graduating_duration_days + 1 > self.easy_duration_days:
            pass
        else:
            self.graduating_duration_days += 1

    def decrement_graduating_duration_days(self):
        if self.graduating_duration_days - 1 < 0:
            pass
        else:
            self.graduating_duration_days -= 1

    def increment_easy_duration_days(self):
        self.easy_duration_days += 1

    def decrement_easy_duration_days(self):
        if self.easy_duration_days - 1 <= self.easy_duration_days:
            pass
        else:
            self.easy_duration_days -= 1
    
    def set_insertion_order_to_sequential(self):
        self.insertion_order = InsertionOrder.SEQUENTIAL
    
    def set_insertion_order_to_random(self):
        self.insertion_order = InsertionOrder.RANDOM
    
    def increase_relearning_steps_minutes(self):
        self.relearning_steps_minutes += 1
    
    def decrease_relearning_steps_minutes(self):
        if self.relearning_steps_minutes - 1 <= 0:
            pass
        else:
            self.relearning_steps_minutes -= 1

    def increase_minumum_interval(self):
        self.minumum_interval += 1
    
    def decrease_minumum_interval(self):
        if self.minumum_interval - 1 <= 0:
            pass
        else:
            self.minumum_interval -= 1

    def increase_leech_threshold(self):
        self.leech_threshold += 1
    
    def decrease_leech_threshold(self):
        if self.leech_threshold - 1 <= 0:
            pass
        else:
            self.leech_threshold -= 1
    
    def set_leech_action_to_tag_only(self):
        self.leech_action = LeechAction.TAG_ONLY

    def set_leech_action_to_suspend_card(self):
        self.leech_action = LeechAction.SUSPEND_CARD
    
    def increase_maximum_answer_seconds(self):
        self.maximum_answer_seconds += 1
    
    def decrease_maximum_answer_seconds(self):
        if self.maximum_answer_seconds - 1 <= 0:
            pass
        else:
            self.maximum_answer_seconds -= 1
    
    def negate_answer_timer(self):
        self.is_answer_time_shown = not(self.is_answer_time_shown)

    def negate_new_siblings_buried(self):
        self.is_new_siblings_buried = not(self.is_new_siblings_buried)

    def negate_review_siblings_buried(self):
        self.is_review_siblings_buried = not(self.is_review_siblings_buried)
    
    def negate_audio_automatically_replayed(self):
        self.is_audio_automatically_replayed = not(self.is_audio_automatically_replayed)

    def negate_question_skipped(self):
        self.is_question_skipped = not(self.is_question_skipped)

    def increment_maximum_interval_days(self):
        self.maximum_interval_days += 1

    def decrement_maximum_interval_days(self):
        if self.maximum_interval_days - 1 <= 0:
            pass
        else:
            self.maximum_interval_days -= 1

    def increment_starting_ease(self):
        self.starting_ease += 0.01
    
    def decrement_starting_ease(self):
        if self.starting_ease - 0.01 <= 0:
            pass
        else:
            self.starting_ease -= 0.01
    
    def increment_easy_bonus(self):
        self.easy_bonus += 0.01
    
    def decrement_easy_bonus(self):
        if self.easy_bonus - 0.01 <= 0:
            pass
        else:
            self.easy_bonus -= 0.01

    def increment_interval_modifier(self):
        self.interval_modifier += 0.01

    def decrement_interval_modifier(self):
        if self.interval_modifier - 0.01 <= 0:
            pass
        else:
            self.interval_modifier -= 0.01

    def increment_hard_interval(self):
        self.hard_interval += 0.01

    def decrement_hard_interval(self):
        if self.hard_interval - 0.01 <= 0:
            pass
        else:
            self.hard_interval -= 0.01

    def increment_new_interval(self):
        self.new_interval += 0.01

    def decrement_new_interval(self):
        if self.new_interval - 0.01 <= 0:
            pass
        else:
            self.new_interval -= 0.01
