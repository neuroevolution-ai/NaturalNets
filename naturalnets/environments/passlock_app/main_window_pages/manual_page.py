
import numpy as np
from naturalnets.environments.gui_app.bounding_box import BoundingBox
from naturalnets.environments.gui_app.page import Page
from naturalnets.environments.gui_app.reward_element import RewardElement
from naturalnets.environments.gui_app.widgets.button import Button
from naturalnets.environments.gui_app.widgets.radio_button_group import RadioButton
from naturalnets.environments.passlock_app.constants import MAIN_PAGE_AREA_BB


class ManualPage(Page, RewardElement):

    STATE_LEN = 0
    #IMG_PATH = os.path.join(IMAGES_PATH, "calculator.png")

    TEXTFIELD_1_BB = BoundingBox(125, 316, 97, 22)
    TEXTFIELD_2_BB = BoundingBox(125, 316, 97, 22)
    CREATE_PW_BB = BoundingBox(9, 112, 99, 22)
    SHOW_PW_BB = BoundingBox(9, 112, 99, 22)


    def __init__(self):
        Page.__init__(self, self.STATE_LEN, MAIN_PAGE_AREA_BB, self.IMG_PATH)
        RewardElement.__init__(self)

        self.is_nameof_password_visible = 0
        self.enter_nameof_password_radiobutton = RadioButton(
            self.TEXTFIELD_1_BB,
            self.enter_nameof_password()
        )

        self.is_secret_password_visible = 0
        self.enter_secret_password_radiobutton = RadioButton(
            self.TEXTFIELD_2_BB,
            self.enter_secret_password()
        )

        self.is_password_visible = 0
        self.show_password_radiobutton = RadioButton(
            self.SHOW_PW_BB,
            self.show_password()
        )

        self.create_pw_button = Button(self.CREATE_PW_BB)

    @property
    def reward_template(self):
        return {

        }
    
    def reset(self):
        pass

    def handle_click(self, click_position: np.ndarray = None):
        if self.create_pw_button.is_clicked_by(click_position):
            self.create_pw_button.handle_click(click_position)    
    
    def render(self, img: np.ndarray):
        img = super().render(img)
        if self.get_state()[0] == 1:  # text is shown
            self.display_text(img)

        return img
    
    def enter_nameof_password():
        pass

    def enter_secret_password():
        pass

    def show_password():
        pass