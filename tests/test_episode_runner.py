import os

import numpy as np

from naturalnets.tools.episode_runner import EpisodeRunner


class TestEpisodeRunner:

    def test_episode_runner(self, ep_runner_test_config, reference_results_dir: str):
        brain_config = ep_runner_test_config[0]
        brain_class = ep_runner_test_config[1]
        env_config = ep_runner_test_config[2]
        env_class = ep_runner_test_config[3]
        enhancer_class = ep_runner_test_config[4]

        reference_file_dir = os.path.join(
            reference_results_dir, "ep_runner"
        )

        reference_file = f"{reference_file_dir}/{brain_config['type']}-{env_config['type']}-{enhancer_class.__name__}.npz"
        reference = np.load(reference_file, allow_pickle=True)

        genomes = reference["genomes"]
        reference_results = reference["results"]

        ep_runner = EpisodeRunner(
            env_class=env_class,
            env_configuration=env_config,
            brain_class=brain_class,
            brain_configuration=brain_config,
            enhancer_class=enhancer_class
        )

        results = list(map(ep_runner.eval_fitness, genomes))

        assert np.array_equal(results, reference_results)
