from naturalnets.environments.app.app import App

WIDTH = 448
HEIGHT = 448

config = {
    "type": "GUIApp",
    "number_time_steps": 100,
    "interactive": True,
    "monkey_tester": False
}

if __name__ == "__main__":

    app = App(config)
    action = None
    while True:
        action = app.render(action)
        if action is None:
            break

        app.step(action)
