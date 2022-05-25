from naturalnets.train import train

configuration = {
    "number_generations": 5000,
    "number_validation_runs": 5,
    "number_rounds": 1,
    "maximum_env_seed": 100000,
    "environment": {
        "type": "DummyApp",
        "number_time_steps": 100,
        "screen_width": 400,
        "screen_height": 400,
        "number_buttons_horizontal": 5,
        "number_buttons_vertical": 5,
        "buttons_size_horizontal": 50,
        "buttons_size_vertical": 30
    },
    "brain": {
        "type": "LSTMNN",
        "hidden_layer_structure": [10],
        "use_bias": True
    },
    "optimizer": {
        "type": "CMA-ES-Deap",
        "population_size": 200,
        "sigma": 1.0
    }
}

train(configuration, results_directory='results')