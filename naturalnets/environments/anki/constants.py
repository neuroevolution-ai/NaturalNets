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