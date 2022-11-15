import numpy as np

REFERENCE_RESULTS_DIR = "tests/reference_results"
REFERENCE_RESULTS_FILE_NAME = "reference_results.npz"


class TestBrains:

    def test_brains(self, brain_test_config):
        input_size = brain_test_config[0]
        output_size = brain_test_config[1]
        brain_config = brain_test_config[2]
        brain_class = brain_test_config[3]

        brain_state = brain_class.generate_brain_state(
            input_size=input_size,
            output_size=output_size,
            configuration=brain_config
        )

        reference_results = np.load(f"{REFERENCE_RESULTS_DIR}/{brain_config['type']}-{REFERENCE_RESULTS_FILE_NAME}")

        individual = reference_results["individual"]

        # noinspection PyCallingNonCallable
        brain = brain_class(
            input_size=input_size,
            output_size=output_size,
            individual=individual,
            configuration=brain_config,
            brain_state=brain_state
        )

        reference_observations = reference_results["observations"]
        reference_actions = reference_results["actions"]
        number_of_interactions = reference_observations.shape[0]

        assert number_of_interactions == reference_actions.shape[0]

        obs = []
        actions = []

        for i in range(number_of_interactions):
            ob = reference_observations[i]
            obs.append(ob)

            action = brain.step(ob)
            actions.append(action)

        assert np.array_equal(np.array(obs, dtype=np.float32), reference_observations)
        assert np.allclose(np.array(actions, dtype=np.float32), reference_actions)
