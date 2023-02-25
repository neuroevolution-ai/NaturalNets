from naturalnets.train import train


def main():
    configuration_app = {
        "number_generations": 5,
        "number_validation_runs": 1,
        "number_rounds": 1,
        "maximum_env_seed": 100000,
        "global_seed": 42,
        "environment": {
            "type": "PasslockApp",
            "number_time_steps": 100,
            "include_fake_bug": False
        },
        "brain": {
            "type": "FeedForwardNN",
            "hidden_layers": [2],
            "neuron_activation": "tanh",
            "neuron_activation_output": "tanh",
            "use_bias": True
        },
        "preprocessing": {
            "observation_standardization": False,
            "calc_ob_stat_prob": 0.01,
            "observation_clipping": False,
            "ob_clipping_value": 5.0
        },
        "enhancer": {
            "type": None
        },
        "optimizer": {
            "type": "CmaEsDeap",
            "population_size": 10,
            "sigma": 0.5
        }
    }

    train(configuration_app, results_directory="results", debug=False, w_and_b_log=False)


if __name__ == "__main__":
    main()