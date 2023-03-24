import os
import tarfile

import wandb


def main():
    """
    For a given sweep, collect the folders for each run of that sleep and create a tar ball with the data.

    In essence, gathers the raw data for all runs of a sweep.

    :return: None
    """
    api = wandb.Api()

    sweep_id = "oh6v8v81"

    sweep_runs = api.sweep(f"neuroevolution-fzi/AST2023/{sweep_id}").runs
    folder_paths = [os.path.join("results", x.name.split("/")[-1]) for x in sweep_runs]

    with tarfile.open(f"sweep-{sweep_id}.tar.gz", "w:gz") as tar:
        for _folder in folder_paths:
            tar.add(_folder)

    print("Done")


if __name__ == "__main__":
    main()
