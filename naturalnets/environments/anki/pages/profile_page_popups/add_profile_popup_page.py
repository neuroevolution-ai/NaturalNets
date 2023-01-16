import os
import random
import numpy as np
from naturalnets.environments.anki.constants import IMAGES_PATH
from naturalnets.environments.anki.pages.name_exists_popup_page import NameExistsPopupPage
from naturalnets.environments.anki.pages.profile_page_popups.five_profiles_popup_page import FiveProfilesPopupPage
from naturalnets.environments.anki.profile import Profile, ProfileDatabase
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button