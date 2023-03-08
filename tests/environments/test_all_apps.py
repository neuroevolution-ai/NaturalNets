from naturalnets.environments.anki.anki_app import AnkiApp
from naturalnets.environments.dummy_app.dummy_app import DummyApp
from naturalnets.environments.passlock_app.passlock_app import PasslockApp


class TestPasslockApp:

    passlock_app = None

    def test_passlock_object_creation(self):
        """
        Test if the PasslockApp is created correctly
        """
        self.passlock_app = PasslockApp({
            "type": "PasslockApp",
            "number_time_steps": 100,
            "include_fake_bug": False
        })

        assert self.passlock_app is not None

    def test_passlock_reset(self):
        """
        Test if the PaslockApp resets the click position to 0,0
        """
        self.passlock_app.click_position_x = 100
        self.passlock_app.click_position_y = 100
        self.passlock_app.reset()
        assert self.passlock_app.click_position_x == 0
        assert self.passlock_app.click_position_y == 0


class TestAnkiApp():

    anki_app = AnkiApp({
        "type": "AnkiApp",
        "number_time_steps": 100,
    })

    def test_anki_reset(self):
        """
        Test if the AnkiApp resets the click position to 0,0
        """
        self.anki_app.click_position_x = 100
        self.anki_app.click_position_y = 100
        self.anki_app.reset()
        assert self.anki_app.click_position_x == 0
        assert self.anki_app.click_position_y == 0


class TestDummyApp():

    dummy_app = DummyApp({
        "type": "DummyApp",
        "number_time_steps": 100,
        "screen_width": 400,
        "screen_height": 400,
        "number_button_columns": 5,
        "number_button_rows": 5,
        "button_width": 50,
        "button_height": 30,
        "fixed_env_seed": True
    })

    def test_dummy_reset(self):
        """
        Test if the DummyApp resets the click position to 0,0
        """
        self.dummy_app.click_position_x = 100
        self.dummy_app.click_position_y = 100
        self.dummy_app.reset()
        assert self.dummy_app.click_position_x == 0
        assert self.dummy_app.click_position_y == 0
