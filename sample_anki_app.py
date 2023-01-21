from naturalnets.train import train

configuration = {
    "number_generations": 5000,
    "number_validation_runs": 50,
    "number_rounds": 5,
    "maximum_env_seed": 100000,
    "environment": {
        "type": "AnkiApp",
        "number_time_steps": 100,
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
