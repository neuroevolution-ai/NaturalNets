from naturalnets.train import train
def main():
    configuration = {
        "number_generations": 100,
        "number_validation_runs": 50,
        "number_rounds": 5,
        "maximum_env_seed": 100000,
        "global_seed": 0,
        "environment": {
            "type": "AnkiApp",
            "number_time_steps": 50
        },
        "brain": {
            "type": "LSTM",
            "hidden_layers": [5],
            "use_bias": True
        },
        "optimizer": {
            "type": "CmaEsDeap",
            "population_size": 5,
            "sigma": 0.5
        },
        "enhancer": {
            "type": "RandomEnhancer"
        },
        "preprocessing": {
           "observation_standardization": False,
           "calc_ob_stat_prob": 0.01,
           "observation_clipping": False,
           "ob_clipping_value": 5.0
        }
    }

    train(configuration, results_directory="results",debug = False,w_and_b_log = False)

if __name__ == "__main__":
    main()
