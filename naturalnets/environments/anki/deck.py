from naturalnets.environments.anki.card import Card
from naturalnets.environments.anki.constants import InsertionOrder,StandardSettingValues,LeechAction,SeparatedBy,DeckOptionAction
from naturalnets.environments.anki.deck import Deck,DeckOption,DeckDatabase
import numpy as np

class Deck():
    
    def __init__(self,name:str,separated_by:SeparatedBy):
        self.name = name
        self.cards: list[Card] = []
        self.current_option: DeckOption = DeckDatabase().decks[0]
        self.seperated_by = separated_by

    def add_card(self,card: Card):
        if self.cards.count(card) != 0:
            self.cards.append(card)
    
    def remove_card(self,card: Card):
        self.cards.remove(card)

    def alter_option(self,action:DeckOptionAction):
        if action.value == DeckOptionAction.INCREMENT_CARD_NUMBER:
            self.current_option.increment_card_number()
        elif action.value == DeckOptionAction.DECREMENT_CARD_NUMBER:
            self.current_option.decrement_card_number()    
        elif action.value == DeckOptionAction.INCREMENT_MAX_REVIEW_NUMBER:
            self.current_option.increment_max_review_number()    
        elif action.value == DeckOptionAction.DECREMENT_MAX_REVIEW_NUMBER:
            self.current_option.decrement_max_review_number()    
        elif action.value == DeckOptionAction.DECREMENT_AGAIN_DURATION_MINUTES:
            self.current_option.decrement_again_duration_minutes()    
        elif action.value == DeckOptionAction.INCREMENT_GOOD_DURATION_MINUTES:
            self.current_option.increment_good_duration_minutes()    
        elif action.value == DeckOptionAction.DECREMENT_GOOD_DURATION_MINUTES:
            self.current_option.decrement_good_duration_minutes()    
        elif action.value == DeckOptionAction.INCREMENT_GRADUATING_DURATION_DAYS:
            self.current_option.increment_graduating_duration_days()    
        elif action.value == DeckOptionAction.DECREMENT_GRADUATING_DURATION_DAYS:
            self.current_option.decrement_graduating_duration_days()    
        elif action.value == DeckOptionAction.INCREMENT_EASY_DURATION_DAYS:
            self.current_option.increment_easy_duration_days()    
        elif action.value == DeckOptionAction.DECREMENT_EASY_DURATION_DAYS:
            self.current_option.decrement_easy_duration_days()    
        elif action.value == DeckOptionAction.SET_INSERTION_ORDER_TO_SEQUENTIAL:
            self.current_option.set_insertion_order_to_sequential()    
        elif action.value == DeckOptionAction.SET_INSERTION_ORDER_TO_RANDOM:
            self.current_option.set_insertion_order_to_random()    
        elif action.value == DeckOptionAction.INCREASE_RELEARNING_STEPS_MINUTES:
            self.current_option.increase_relearning_steps_minutes()    
        elif action.value == DeckOptionAction.DECREASE_RELEARNING_STEPS_MINUTES:
            self.current_option.decrease_relearning_steps_minutes()    
        elif action.value == DeckOptionAction.INCREASE_MINUMUM_INTERVAL:
            self.current_option.increase_minumum_interval()    
        elif action.value == DeckOptionAction.DECREASE_MINUMUM_INTERVAL:
            self.current_option.decrease_minumum_interval()    
        elif action.value == DeckOptionAction.INCREASE_LEECH_THRESHOLD:
            self.current_option.increase_leech_threshold()    
        elif action.value == DeckOptionAction.DECREASE_LEECH_THRESHOLD:
            self.current_option.decrease_leech_threshold()    
        elif action.value == DeckOptionAction.SET_LEECH_ACTION_TO_TAG_ONLY:
            self.current_option.set_leech_action_to_tag_only()    
        elif action.value == DeckOptionAction.SET_LEECH_ACTION_TO_SUSPEND_CARD:
            self.current_option.set_leech_action_to_suspend_card()    
        elif action.value == DeckOptionAction.INCREASE_MAXIMUM_ANSWER_SECONDS:
            self.current_option.increase_maximum_answer_seconds()    
        elif action.value == DeckOptionAction.DECREASE_MAXIMUM_ANSWER_SECONDS:
            self.current_option.decrease_maximum_answer_seconds()    
        elif action.value == DeckOptionAction.NEGATE_ANSWER_TIMER:
            self.current_option.negate_answer_timer()    
        elif action.value == DeckOptionAction.NEGATE_NEW_SIBLINGS_BURIED:
            self.current_option.negate_new_siblings_buried()    
        elif action.value == DeckOptionAction.NEGATE_REVIEW_SIBLINGS_BURIED:
            self.current_option.negate_review_siblings_buried()    
        elif action.value == DeckOptionAction.NEGATE_AUDIO_AUTOMATICALLY_REPLAYED:
            self.current_option.negate_audio_automatically_replayed()    
        elif action.value == DeckOptionAction.NEGATE_QUESTION_SKIPPED:
            self.current_option.negate_question_skipped()    
        elif action.value == DeckOptionAction.INCREMENT_MAXIMUM_INTERVAL_DAYS:
            self.current_option.increment_maximum_interval_days()    
        elif action.value == DeckOptionAction.DECREMENT_MAXIMUM_INTERVAL_DAYS:
            self.current_option.decrement_maximum_interval_days()    
        elif action.value == DeckOptionAction.INCREMENT_STARTING_EASE:
            self.current_option.increment_starting_ease()    
        elif action.value == DeckOptionAction.DECREMENT_STARTING_EASE:
            self.current_option.decrement_starting_ease()    
        elif action.value == DeckOptionAction.INCREMENT_EASY_BONUS:
            self.current_option.increment_easy_bonus()    
        elif action.value == DeckOptionAction.DECREMENT_EASY_BONUS:
            self.current_option.decrement_easy_bonus()    
        elif action.value == DeckOptionAction.INCREMENT_INTERVAL_MODIFIER:
            self.current_option.increment_interval_modifier()    
        elif action.value == DeckOptionAction.DECREMENT_INTERVAL_MODIFIER:
            self.current_option.decrement_interval_modifier()    
        elif action.value == DeckOptionAction.INCREMENT_HARD_INTERVAL:
            self.current_option.increment_hard_interval()    
        elif action.value == DeckOptionAction.DECREMENT_HARD_INTERVAL:
            self.current_option.decrement_hard_interval()    
        elif action.value == DeckOptionAction.INCREMENT_NEW_INTERVAL:
            self.current_option.increment_new_interval()    
        elif action.value == DeckOptionAction.DECREMENT_NEW_INTERVAL:
            self.current_option.decrement_new_interval()    
        
    def convert_text_to_card(self,file_path:str,separated_by: SeparatedBy):
        f = open(file_path,'r')
        lines:list[str] = f.readlines()  
        for line in lines:
            self.cards.append(Card(line.split(separated_by)[0],line.split(separated_by)[1]))

    def push_to_database(self,deck :Deck):
        DeckDatabase().decks.append(deck)
            
class DeckOption():

    def __init__(self, name: str):
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

class DeckOptionDatabase():
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeckOptionDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.available_decks = [DeckOption("Default")]

    def add_deck_option(self,deck_option_name: str):
        if self.available_decks.count(DeckOption(deck_option_name) == 0):
            self.available_decks.append(DeckOption(deck_option_name))
        else:
            print("Deck option with same name exists")
    
    def delete_deck_option(self,deck_option_name: str):
        if deck_option_name == "Default":
            print("Default deck option can not be deleted")
        elif self.available_decks.count(DeckOption(deck_option_name) != 0):
            self.available_decks.remove(DeckOption(deck_option_name))
        else:
            print("Deck option with such a name does not exist")

    def rename_deck_option(self,previous_deck_option_name: str,new_deck_option_name: str):
        if previous_deck_option_name == "Default":
            print("Default deck option can not be renamed")
            return
        for deck in self.available_decks:
            if(previous_deck_option_name == deck.name):
                deck.name = new_deck_option_name
                return

    def clone_deck_option(self,deck_option_name: str,deck_option: DeckOption):
        deck_option.name = deck_option_name
        self.add_deck_option(deck_option)

class DeckDatabase():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DeckDatabase, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.decks: list[Deck] = []
    