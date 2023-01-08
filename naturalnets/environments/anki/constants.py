from enum import Enum

IMAGES_PATH: str = "naturalnets/environments/anki/img/"
PREDEFINED_DECKS_PATH: str = "naturalnets/environments/anki/decks/predefined_decks/"
EXPORTED_DECKS_PATH: str = "naturalnets/environments/anki/decks/exported_decks/"
class InsertionOrder(Enum):
    
    SEQUENTIAL = "Sequential",
    RANDOM = "Random"

class LeechAction(Enum):
    
    SUSPEND_CARD = "Suspend Card",
    TAG_ONLY = "Tag Only"

class StandardSettingValues(Enum):
    
    NEW_CARDS_PER_DAY = 20
    MAX_REVIEWS_PER_DAY = 200
    AGAIN_LEARNING_STEP_MIN = 1
    GOOD_LEARNING_STEP_MIN = 10
    GRADUATING_INTERVAL_STEP_DAY = 1
    EASY_INTERVAL_STEP_DAY = 4
    INSERTION_ORDER = "Sequential"
    RELEARNING_STEPS_MIN = 10
    MIN_INTERVAL = 1
    LEECH_THRESHOLD = 8
    LEECH_ACTION = "Tag Only"
    MAX_ANSWER_SECONDS = 60
    SHOW_ANSWER_TIME = False
    BURY_NEW_SIBLINGS = False
    BURY_REVIEW_SIBLINGS = False
    PLAY_AUDIO_AUTOMATICALLY = False
    SKIP_QUESTION_WHEN_REPLAYING_ANSWER = False
    MAX_INTERVAL_DAYS = 36500
    STARTING_EASE = 2.50
    EASY_BONUS = 1.30
    INTERVAL_MODIFIER = 1.00
    HARD_INTERVAL = 1.20
    NEW_INTERVAL = 0.00

class FlagColour(Enum):
    
    RED = "Red"
    ORANGE = "Orange"
    GREEN = "Green"
    BLUE = "Blue"
    PINK = "Pink"
    TURQUOISE = "Turquoise"
    PURPLE = "Purple"
class DeckOptionAction(Enum):
    INCREMENT_CARD_NUMBER = "increment_card_number"
    DECREMENT_CARD_NUMBER = "decrement_card_number"
    INCREMENT_MAX_REVIEW_NUMBER = "increment_max_review_number"
    DECREMENT_MAX_REVIEW_NUMBER = "decrement_max_review_number"
    INCREMENT_AGAIN_DURATION_MINUTES = "increment_again_duration_minutes"
    DECREMENT_AGAIN_DURATION_MINUTES = "decrement_again_duration_minutes"
    INCREMENT_GOOD_DURATION_MINUTES = "increment_good_duration_minutes"
    DECREMENT_GOOD_DURATION_MINUTES = "decrement_good_duration_minutes"
    INCREMENT_GRADUATING_DURATION_DAYS = "increment_graduating_duration_days"
    DECREMENT_GRADUATING_DURATION_DAYS = "decrement_graduating_duration_days"
    INCREMENT_EASY_DURATION_DAYS = "increment_easy_duration_days"
    DECREMENT_EASY_DURATION_DAYS = "decrement_easy_duration_days"
    SET_INSERTION_ORDER_TO_SEQUENTIAL = "set_insertion_order_to_sequential"
    SET_INSERTION_ORDER_TO_RANDOM = "set_insertion_order_to_random"
    INCREASE_RELEARNING_STEPS_MINUTES = "increase_relearning_steps_minutes"
    DECREASE_RELEARNING_STEPS_MINUTES = "decrease_relearning_steps_minutes"
    INCREASE_MINUMUM_INTERVAL = "increase_minumum_interval"
    DECREASE_MINUMUM_INTERVAL = "decrease_minumum_interval"
    INCREASE_LEECH_THRESHOLD = "increase_leech_threshold"
    DECREASE_LEECH_THRESHOLD = "decrease_leech_threshold"
    SET_LEECH_ACTION_TO_TAG_ONLY = "set_leech_action_to_tag_only"
    SET_LEECH_ACTION_TO_SUSPEND_CARD =  "set_leech_action_to_suspend_card"
    INCREASE_MAXIMUM_ANSWER_SECONDS = "increase_maximum_answer_seconds"
    DECREASE_MAXIMUM_ANSWER_SECONDS = "decrease_maximum_answer_seconds"
    NEGATE_ANSWER_TIMER = "negate_answer_timer"
    NEGATE_NEW_SIBLINGS_BURIED = "negate_new_siblings_buried"
    NEGATE_REVIEW_SIBLINGS_BURIED = "negate_review_siblings_buried"
    NEGATE_AUDIO_AUTOMATICALLY_REPLAYED = "negate_audio_automatically_replayed"
    NEGATE_QUESTION_SKIPPED = "negate_question_skipped"
    INCREMENT_MAXIMUM_INTERVAL_DAYS = "increment_maximum_interval_days"
    DECREMENT_MAXIMUM_INTERVAL_DAYS = "decrement_maximum_interval_days"
    INCREMENT_STARTING_EASE = "increment_starting_ease"
    DECREMENT_STARTING_EASE = "decrement_starting_ease"
    INCREMENT_EASY_BONUS = "increment_easy_bonus"
    DECREMENT_EASY_BONUS = "decrement_easy_bonus"
    INCREMENT_INTERVAL_MODIFIER = "increment_interval_modifier"
    DECREMENT_INTERVAL_MODIFIER = "decrement_interval_modifier"
    INCREMENT_HARD_INTERVAL = "increment_hard_interval"
    DECREMENT_HARD_INTERVAL = "decrement_hard_interval"
    INCREMENT_NEW_INTERVAL = "increment_new_interval"
    DECREMENT_NEW_INTERVAL = "decrement_new_interval"

class ProfileNames(Enum):
    ALICE = "Alice"
    BOB = "Bob"
    CAROL = "Carol"
    DENNIS = "Dennis"    
    EVA = "Eva"

class OptionNames(Enum):
    OPTION_1 = "Option 1"
    OPTION_2 = "Option 2"
    OPTION_3 = "Option 3"
    OPTION_4 = "Option 4"
    OPTION_5 = "Option 5"
    
class DeckNames(Enum):
    DECK_NAME_1 = "Deck Name 1"
    DECK_NAME_2 = "Deck Name 2"
    DECK_NAME_3 = "Deck Name 3"
    DECK_NAME_4 = "Deck Name 4"
    DECK_NAME_5 = "Deck Name 5"

class DeckImportName(Enum):
    DUTCH_NUMBERS = "Dutch numbers 0-100"
    ITALIAN_NUMBERS = "Italian numbers 0-100"
    GERMAN_NUMBERS = "German numbers 0-100"
