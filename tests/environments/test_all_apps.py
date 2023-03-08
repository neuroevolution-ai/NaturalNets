
from naturalnets.environments.anki.anki_app import AnkiApp
from naturalnets.environments.dummy_app.dummy_app import DummyApp
from naturalnets.environments.passlock_app.passlock_app import PasslockApp
from naturalnets.tools.utils import rescale_values


class TestPasslockApp:

    def test_passlock_app_reward(self, test_coordinates_and_rewards):
        """
        Test if the GUIApp environment returns the correct reward for a series of interactions
        """
        for interaction_sequence in test_coordinates_and_rewards:
            passlock_app = PasslockApp({
                "type": "GUIApp",
                "number_time_steps": len(interaction_sequence),
                "include_fake_bug": False
            })
            passlock_app.reset()
            for interaction in interaction_sequence:
                # Recorded interactions are integer coordinates, but all environments require floats between [-1, 1]
                _, rew, _, _ = passlock_app.step([rescale_values(interaction[0], previous_low=0, previous_high=passlock_app.get_screen_width(), new_high=1, new_low=-1),
                                                  rescale_values(interaction[1], previous_low=0, previous_high=passlock_app.get_screen_height(), new_high=1, new_low=-1)])
                # Compare reward coming from the environment with the recorded, ground truth reward
                assert rew == interaction[2]


class TestAnkiApp():

    def test_anki_app_reward(self, test_coordinates_and_rewards):
        """
        Test if the GUIApp environment returns the correct reward for a series of interactions
        """
        for interaction_sequence in test_coordinates_and_rewards:
            anki_app = AnkiApp({
                "type": "GUIApp",
                "number_time_steps": len(interaction_sequence)
            })
            anki_app.reset()
            for interaction in interaction_sequence:
                # Recorded interactions are integer coordinates, but all environments require floats between [-1, 1]
                _, rew, _, _ = anki_app.step([rescale_values(interaction[0], previous_low=0, previous_high=anki_app.get_screen_width(), new_high=1, new_low=-1),
                                              rescale_values(interaction[1], previous_low=0, previous_high=anki_app.get_screen_height(), new_high=1, new_low=-1)])
                # Compare reward coming from the environment with the recorded, ground truth reward
                assert rew == interaction[2]


class TestDummyApp():

    def test_dummy_app_reward(self, test_coordinates_and_rewards):
        """
        Test if the GUIApp environment returns the correct reward for a series of interactions
        """
        for interaction_sequence in test_coordinates_and_rewards:
            dummy_app = DummyApp({
                "type": "DummyApp",
                "number_time_steps": len(interaction_sequence),
                "screen_width": 400,
                "screen_height": 400,
                "number_button_columns": 5,
                "number_button_rows": 5,
                "button_width": 50,
                "button_height": 30,
                "fixed_env_seed": True
            })
            dummy_app.reset()
            for interaction in interaction_sequence:
                # Recorded interactions are integer coordinates, but all environments require floats between [-1, 1]
                _, rew, _, _ = dummy_app.step([rescale_values(interaction[0], previous_low=0, previous_high=dummy_app.get_screen_width(), new_high=1, new_low=-1),
                                              rescale_values(interaction[1], previous_low=0, previous_high=dummy_app.get_screen_height(), new_high=1, new_low=-1)])
                # Compare reward coming from the environment with the recorded, ground truth reward
                # Compare reward coming from the environment with the recorded, ground truth reward
                assert rew == interaction[2]
