import numpy as np

from naturalnets.environments import GUIApp
from naturalnets.tools.utils import rescale_values


class TestGUIApp:

    def test_gui_app_reward(self, test_coordinates_and_rewards):
        """
        Test if the GUIApp environment returns the correct reward for a series of interactions
        """

        max_number_time_steps = np.max([x.size for x in test_coordinates_and_rewards])

        gui_app = GUIApp({
            "type": "GUIApp",
            "number_time_steps": max_number_time_steps,
            "include_fake_bug": False
        })

        for interaction_sequence in test_coordinates_and_rewards:
            gui_app.reset()

            for interaction in interaction_sequence:
                # Recorded interactions are integer coordinates, but all environments require floats between [-1, 1]
                _, rew, _, _ = gui_app.step(
                    rescale_values(interaction[:2], previous_low=0, previous_high=447, new_low=-1, new_high=1)
                )

                # Compare reward coming from the environment with the recorded, ground truth reward
                assert rew == interaction[2]
