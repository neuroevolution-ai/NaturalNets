def deprecate_environment(environment_name: str):
    supported_environments = [
        "DummyApp",
        "GUIApp",
        "GymMujoco"
    ]
    raise DeprecationWarning(f"The environment '{environment_name}' has been deprecated, please use one of the "
                             f"following supported environments: {supported_environments!r}.")
