from naturalnets.environments import AnkiApp
from naturalnets.tools.utils import rescale_values


class TestAnkiApp:

    def test_anki_app_reward(self, test_coordinates_and_rewards):
        """
        Test if the AnkiApp environment returns the correct reward for a series of interactions
        """

        for interaction_sequence in test_coordinates_and_rewards:
            gui_app = AnkiApp({
                "type": "AnkiApp",
                "number_time_steps": len(interaction_sequence),
            })

            gui_app.reset()

            for interaction in interaction_sequence:
                # Recorded interactions are integer coordinates, but all environments require floats between [-1, 1]
                _, rew, _, _ = gui_app.step(
                    rescale_values(interaction[:2], previous_low=0, previous_high=834, new_low=-1, new_high=1)
                )

                # Compare reward coming from the environment with the recorded, ground truth reward
                assert rew == interaction[2]
