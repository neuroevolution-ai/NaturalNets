from enum import Enum

IMAGES_PATH: str = "naturalnets/environments/anki/img/"
PREDEFINED_DECKS_PATH: str = "naturalnets/environments/anki/decks/predefined_decks/"
EXPORTED_DECKS_PATH: str = "naturalnets/environments/anki/decks/exported_decks/"

"""
Possible profile names
"""


class ProfileNames(Enum):
    ALICE = "Alice"
    BOB = "Bob"
    CAROL = "Carol"
    DENNIS = "Dennis"
    EVA = "Eva"


"""
Possible deck names
"""


class DeckNames(Enum):
    DECK_NAME_1 = "Deck Name 1"
    DECK_NAME_2 = "Deck Name 2"
    DECK_NAME_3 = "Deck Name 3"
    DECK_NAME_4 = "Deck Name 4"
    DECK_NAME_5 = "Deck Name 5"


"""
Possible decks that can be imported
"""


class DeckImportName(Enum):
    DUTCH_NUMBERS = "Dutch numbers 0-100"
    ITALIAN_NUMBERS = "Italian numbers 0-100"
    GERMAN_NUMBERS = "German numbers 0-100"


"""
Possible anki languages
"""


class AnkiLanguages(Enum):
    ENGLISH = "English"
    GERMAN = "German"
    SPANISH = "Spanish"


"""
List of video drivers. Has nothing to do with the logic of the application but is a filler in the preferences page
"""


class VideoDriver(Enum):
    OPENGL = "Video driver: OpenGL (faster, may cause issues)"
    ANGLE = "Video driver: ANGLE (may work better than OpenGL)"
    SOFTWARE = "Video driver: Software (slower)"


"""
List of deck add types. Has nothing to do with the logic of the application but is a filler in the preferences page
"""


class DeckAddType(Enum):
    ADD_TO_CURRENT = "When adding, default to current deck"
    CHANGE_DECK = "Change deck depending on note type"


"""
List of voice recorders. Has nothing to do with the logic of the application but is a filler in the preferences page
"""


class VoiceRecorder(Enum):
    QT = "Voice recording driver: Qt"
    PY_AUDIO = "Voice recording driver: PyAudio"
