from enum import Enum

IMAGES_PATH: str = "naturalnets/environments/anki/img/"

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

class AboutAnkiText(Enum):
    
    ANKI_FIRST_LINE = "Anki is a friendly, intelligent spaced learning system. It's free and open source."
    ANKI_SECOND_LINE = "Anki is licenced under the AGPL3 licence. Please see the licence file in the source distribution for more information."
    ANKI_THIRD_LINE = "Version 2.1.49 (dc80804a)"
    ANKI_FOURTH_LINE = "Python 3.8.6 Qt 5.14.2 PyQt 5.14.2 \n"
    ANKI_FIFTH_LINE = "Written by Damien Elmes, with patches, translation, testing and design from:"
    ANKI_CONTRIBUTORS = ["AMBOSS MD Inc.","ANH","Aaron Harsh", "Alan Du", "Alex Fraser", "Andreas Klauer", "Andrew Wright", "Aristotelis P", "Arman High", "Arthur Milchior", "Bernhard Ibertsberger", "C. van Rooyen", "Charlene Barina", "Christian Krause", "Christian Rusche", "Dave Druelinger", "David Bailey", "David Smith", "Dmitry Mikheev", "Dotan Cohen", "Emilio Wuerges", "Emmanuel Jarri", "Erez Volk", "Evandro Coan", "Frank Harper", "Gregor Skumavc",
    "Guillem Palau Salvà", "Gustavo Costa", "H. Mijail", "Henrik Enggaard Hansen", "Houssam Salem", "Ian Lewis", "Ijgnd", "Immanuel Asmus", "Iroiro", "Jarvik7", "Jin Eun-Deok", "Jo Nakashima", "Johanna Lindh", "Joseph Lorimer", "Julien Baley", "Junseo Park", "Jussi Määttä", "Kieran Clancy", "LaC", "Laurent Steffan", "Luca Ban", "Luciano Esposito", "Marco Giancotti", "Marcus Rubeus", "Mari Egami", "Mark Wilbur", "Matthew Duggan", "Matthew Holtz",
    "Meelis Vasser", "Michael Jürges", "Michael Keppler", "Michael Montague", "Michael Penkov", "Michal Čadil", "Morteza Salehi", "Nathanael Law", "Nguyễn Hào Khôi", "Nick Cook", "Niklas Laxström", "Norbert Nagold", "Ole Guldberg", "Pcsl88", "Petr Michalec", "Piotr Kubowicz", "Rai (Michael Pokorny)", "Richard Colley", "Roland Sieker", "RumovZ", "Samson Melamed", "Silja Ijas", "Snezana Lukic", "Soren Bjornstad", "Stefaan De Pooter", "Susanna Björverud",
    "Sylvain Durand", "Tacutu", "Thomas Kahn", "Timm Preetz", "Timo Paulssen", "Tobias Predel", "Ursus", "Victor Suba", "Volker Jansen", "Volodymyr Goncharenko", "Xtru", "zjosua", "Ádám Szegi","余时行", "叶峻峣", "学习骇客", "赵金鹏", "黃文龍"]
    ANKI_PRELAST_LINE = "If you have contributed and are not on this list, please get in touch."
    ANKI_LAST_LINE = "A big thanks to all the people who have provided suggestions, bug reports, translations and donations."

class SeparatedBy(Enum):
    SPACE = " "
    TAB = "\t"

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

    
    
    
    
    
    
    
    
    
    
    
    
    
