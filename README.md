## Setup

Run `pip install git+https://github.com/neuroevolution-ai/NaturalNets.git` to add this package to your python environment

## Examples

Single training run:

```python
from naturalnets.train import train

configuration = {
    "number_generations": 200,
    "number_validation_runs": 50,
    "number_rounds": 3,
    "maximum_env_seed": 100000,
    "fixed_env_seed": False,
    "environment": {
        "type": "GymMujoco",
        "name": "InvertedDoublePendulum-v2"
    },
    "brain": {
        "type": "CTRNN",
        "delta_t": 0.05,
        "differential_equation": "NaturalNet",
        "number_neurons": 5,
        "v_mask": "dense",
        "w_mask": "dense",
        "t_mask": "dense",
        "clipping_range": 3.0,
        "set_principle_diagonal_elements_of_W_negative": True,
        "optimize_x0": True,
        "alpha": 0.0
    },
    "optimizer": {
        "type": "CmaEsDeap",
        "population_size": 200,
        "sigma": 1.0
    }
}

train(configuration, results_directory="results")
```

More complex example of a random hyperparameter search. This experiment executes an indefinite number of training runs
until it gets actively interrupted:

```python
from naturalnets.train import train
import os
import random
from pathlib import Path

while True:

    environment_configuration = dict()
    environment_configuration["type"] = "GymMujoco"
    environment_configuration["name"] = random.choice(["InvertedDoublePendulum-v2", "InvertedPendulum-v2", "Reacher-v2", "Swimmer-v2", "Hopper-v2", "Walker2d-v2", "HalfCheetah-v2"])

    brain_configuration = dict()
    brain_configuration["type"] = random.choice(["CTRNN", "CTRNN", "CTRNN", "CTRNN", "ELMANNN", "GRUNN", "LSTMNN", "FFNN"])

    if(brain_configuration["type"] == "CTRNN"):
        brain_configuration["differential_equation"] = random.choice(["NaturalNet", "LiHoChow2005"])

        if(brain_configuration["differential_equation"] == "NaturalNet"):
            brain_configuration["set_principle_diagonal_elements_of_W_negative"] = random.choice([False, True])

        elif(brain_configuration["differential_equation"] == "LiHoChow2005"):
            brain_configuration["set_principle_diagonal_elements_of_W_negative"] = False
            brain_configuration["alpha"] = random.choice([0.0, 0.1, 0.01])

        else:
            raise RuntimeError("No valid CTRNN differential equation")

        brain_configuration["delta_t"] = 0.05
        brain_configuration["number_neurons"] = random.choice([5, 10, 20, 50])
        brain_configuration["clipping_range"] = random.choice([1.0, 3.0, float('inf'), float('inf')])
        brain_configuration["optimize_x0"] = random.choice([False, True])

    elif(brain_configuration["type"] == "ELMANNN" or brain_configuration["type"] == "GRUNN" or brain_configuration["type"] == "LSTMNN"):
        brain_configuration["hidden_layer_structure"] = random.choice([[5], [10], [20], [50]])
        brain_configuration["use_bias"] = random.choice([False, True])

    elif(brain_configuration["type"] == "FFNN"):
        brain_configuration["hidden_layers"] = random.choice([[5, 5], [10, 10], [20, 20], [50, 50]])
        brain_configuration["neuron_activation"] = "tanh"
        brain_configuration["neuron_activation_output"] = "tanh"
        brain_configuration["use_bias"] = random.choice([False, True])

    else:
        raise RuntimeError("No valid brain type")

    optimizer_configuration = dict()
    optimizer_configuration["type"] = "CMA-ES-Deap"
    optimizer_configuration["population_size"] = 200
    optimizer_configuration["sigma"] = random.choice([0.5, 1.0, 2.0])

    configuration = dict()
    configuration["number_generations"] = 2500
    configuration["number_validation_runs"] = 50
    configuration["number_rounds"] = 3
    configuration["maximum_env_seed"] = 100000
    configuration["environment"] = environment_configuration
    configuration["brain"] = brain_configuration
    configuration["optimizer"] = optimizer_configuration

    print(configuration)

    # Path of current script
    script_directory = Path(__file__).parent.absolute()

    train(configuration, results_directory=os.path.join(script_directory, 'Simulation_Results'))
```

## Training using GPU

1. Uninstall `deap`
2. Run `pip install git+https://github.com/neuroevolution-ai/deap@eigenvalues-on-gpu` 
3. Run `pip install cupy-cuda101` if you have a GPU with CUDA 10.1 (if you have another version check the [CuPy website](https://cupy.dev/))
4. Then the eigenvalue calculation should happen on the GPU

## Inspecting Logs using TensorBoard

1. Make sure TensorBoard is installed with `pip install -U -r requirements.txt`
2. On the Terminal run `tensorboard --logdir results/` to view all results of the experiments in Tensorboard
    - Alternatively, run `tensorboard --logdir EXPLICIT_EXP_DIR`, to view the results of a specific experiment,
    where `EXPLICIT_EXP_DIR` is the path to that experiment's logs
3. In a browser, navigate to `http://localhost:6006/`

## Logging to Weights & Biases

- Create a Weights and Biases account
- Install it with `pip install wandb` (it is also in our `requirements.txt`)
- Log in by running `wandb login`, and paste your API key from [https://wandb.ai/authorize](https://wandb.ai/authorize)
- Optional: Edit the `entity` and `project` parameters for the `wandb.init()` call in `train.py`
  - These specify where the values are logged, where `entity` is your WandB username or organization and `project`
  is the name of the project in that entity

### Using Hyperparameter Sweeps

- Quick way to initialize hyperparameter searches
- Copy `naturalnets/configurations/sweep_configurations/DefaultSweep.json` and edit the new file to confiure the sweep
  - Use the `parameters` key to configure the training configuration
  - Each key under `parameters` maps to a key of our training configuration
  - Nested dicts, for example for the environment, brain etc., need to have another `parameters` key, for example:
  ```json
    {
        "parameters": {
            ...
            "number_rounds": {"value":  3},
            ...
            "environment": {
                "parameters": {
                    "type": {"value": "GUIApp"},
                    ...
                }
            }
        }
    }
  ```
  - Each parameter can be configured to have a specific value (`"value": SPECIFIC_VALUE`),
  multiple values (`"values": [VALUE1, VALUE2, ...]` (note the plural `values` as the key)), or more
  advanced mathematical distributions, etc. Read more on this in the
  [WandB Documentation](https://docs.wandb.ai/guides/sweeps/define-sweep-configuration#parameters)
- Create the sweep by running
`wandb sweep naturalnets/configurations/sweep_configurations/YOUR-SWEEP-CONFIG.json`
- Copy the **full** sweep path of the form `ENTITY/PROJECT/SWEEP_ID`
- Run the sweep agent to start experiments
  - Run `PYTHONPATH=$(pwd) python naturalnets/train.py -s ENTITY/PROJECT/SWEEP_ID`
  - If you use a grid search, the agent runs experiments until the grid search is finished
  - If you use a random search and want to limit the number of experiments, use `-sc NUM_EXPERIMENTS`,
  i.e. `PYTHONPATH=$(pwd) python naturalnets/train.py -s ENTITY/PROJECT/SWEEP_ID -sc NUM_EXPERIMENTS`

## Monkey Testing

- Run `PYTHONPATH=$(pwd) python monkey_tester/monkey_tester.py -c PATH_TO_MONKEY_CONFIG` to start the monkey
tester
- A default configuration is found in `monkey_tester/configurations/Configuration.json`. Details for the parameters
are found in the `MonkeyTesterCfg` class in `monkey_tester/monkey_tester.py`