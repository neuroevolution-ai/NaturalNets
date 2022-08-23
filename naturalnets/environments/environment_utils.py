def deprecate_environment(_environment_init_func):
    supported_environments = [
        "DummyApp",
        "GUIApp",
        "GymMujoco"
    ]
    raise DeprecationWarning("This environment has been deprecated, please use one of the following supported "
                             f"environments: {supported_environments!r}.")
