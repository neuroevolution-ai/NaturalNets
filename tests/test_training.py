import json
import os
import shutil
from tempfile import TemporaryDirectory
from typing import Tuple

import numpy as np

from naturalnets.train import train

REFERENCE_RESULTS_DIR = "tests/reference_results"


class TestTraining:

    @staticmethod
    def _compare_json_files(filename: str, reference_dir: str, train_dir: str):
        with open(os.path.join(reference_dir, filename), "r") as ref_file:
            with open(os.path.join(train_dir, filename), "r") as train_file:
                ref_dict = json.load(ref_file)
                train_dict = json.load(train_file)

                if filename == "Log.json":
                    # Last entry of the log contains elapsed time and CPU info, which should not be compared
                    ref_dict = ref_dict[:-1]
                    train_dict = train_dict[:-1]

                    # Removed "elapsed_time" from the log because that is very likely to be different but is indifferent
                    # to the training results, i.e. it should not be compared in this test
                    for gen in ref_dict:
                        del gen["elapsed_time"]

                    for gen in train_dict:
                        del gen["elapsed_time"]

                assert ref_dict == train_dict

    @staticmethod
    def _compare_numpy_files(filename: str, reference_dir: str, train_dir: str):
        reference_file = os.path.join(reference_dir, filename)
        train_file = os.path.join(train_dir, filename)

        # Only CTRNNs store the brain state, thus check if this is indeed so. Otherwise, check if the train file
        # also does not exist
        if os.path.exists(reference_file):
            ref_numpy_file = np.load(reference_file)
            train_numpy_file = np.load(train_file)

            if isinstance(ref_numpy_file, np.ndarray):
                assert np.array_equal(ref_numpy_file, train_numpy_file)
            else:
                for key in ref_numpy_file.keys():
                    assert np.array_equal(ref_numpy_file[key], train_numpy_file[key])
        else:
            assert not os.path.exists(train_file)

    def test_training(self, train_config: Tuple[dict, str, str, str]):
        train_dict = train_config[0]
        chosen_brain = train_config[1]
        chosen_optimizer = train_config[2]
        chosen_enhancer = train_config[3]

        with TemporaryDirectory() as temp_dir:
            train(train_dict, results_directory=temp_dir, debug=False, w_and_b_log=False)

            temp_train_dir_content = os.listdir(temp_dir)
            assert len(temp_train_dir_content) == 1
            train_dir = os.path.join(temp_dir, temp_train_dir_content[0])

            reference_dir = os.path.join(REFERENCE_RESULTS_DIR, chosen_brain, chosen_optimizer, chosen_enhancer)

            self._compare_json_files("Configuration.json", reference_dir, train_dir)
            self._compare_json_files("Log.json", reference_dir, train_dir)
            self._compare_numpy_files("Brain_State.npz", reference_dir, train_dir)
            self._compare_numpy_files("Best_Genome.npy", reference_dir, train_dir)

    @staticmethod
    def _save_train_results(chosen_brain, chosen_optimizer, chosen_enhancer, tempdir):
        """
        Helper function to store training results. Can be used if a new brain, optimizer, etc. shall be added to the
        train test, for the creation of the initial reference files.
        """
        sub_temp_dirs = os.listdir(tempdir)
        assert len(sub_temp_dirs) == 1
        training_dir = os.path.join(tempdir, sub_temp_dirs[0])

        subdir = os.path.join(REFERENCE_RESULTS_DIR, chosen_brain, chosen_optimizer, chosen_enhancer)
        os.makedirs(subdir, exist_ok=False)

        shutil.copy(os.path.join(training_dir, "Configuration.json"), subdir)
        shutil.copy(os.path.join(training_dir, "Log.json"), subdir)
        shutil.copy(os.path.join(training_dir, "Best_Genome.npy"), subdir)
        shutil.copy(os.path.join(training_dir, "Brain_State.npz"), subdir)
