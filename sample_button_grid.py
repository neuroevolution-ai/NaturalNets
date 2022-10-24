from naturalnets.train import train

configuration = {
    "number_generations": 5000,
    "number_validation_runs": 50,
    "number_rounds": 5,
    "maximum_env_seed": 100000,
    "environment": {
        "type": "DummyApp",
        "number_time_steps": 100,
        "screen_width": 400,
        "screen_height": 400,
        "number_button_columns": 5,
        "number_button_rows": 5,
        "button_width": 50,
        "button_height": 30,
        "fixed_env_seed": True
    },
    "brain": {
        "type": "LSTM",
        "hidden_layers": [10],
        "use_bias": True
    },
    "optimizer": {
        "type": "CmaEsDeap",
        "population_size": 200,
        "sigma": 0.5
    },
    "enhancer": {
        "type": "RandomEnhancer"
    }
}

train(configuration, results_directory="results")
