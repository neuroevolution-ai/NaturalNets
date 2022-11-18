import numpy as np


class TestBrains:

    def test_brains(self, brain_test_config, reference_results_dir: str, reference_results_file_name: str):
        input_size = brain_test_config[0]
        output_size = brain_test_config[1]
        brain_config = brain_test_config[2]
        brain_class = brain_test_config[3]

        brain_state = brain_class.generate_brain_state(
            input_size=input_size,
            output_size=output_size,
            configuration=brain_config
        )

        reference_results = np.load(f"{reference_results_dir}/{brain_config['type']}-{reference_results_file_name}")

        individual = reference_results["individual"]

        # noinspection PyCallingNonCallable
        brain = brain_class(
            individual=individual,
            configuration=brain_config,
            brain_state=brain_state,
            env_observation_size=input_size,
            env_action_size=output_size,
            ob_mean=None,
            ob_std=None
        )

        brain.reset(rng_seed=0)

        reference_observations = reference_results["observations"]
        reference_actions = reference_results["actions"]
        number_of_interactions = reference_observations.shape[0]

        assert number_of_interactions == reference_actions.shape[0]

        observations = []
        actions = []

        for i in range(number_of_interactions):
            ob = reference_observations[i]
            observations.append(ob)

            action, _ = brain.step(ob)
            actions.append(action)

        observations = np.array(observations)
        actions = np.array(actions)

        assert np.array_equal(observations, reference_observations)
        assert np.array_equal(actions, reference_actions)
