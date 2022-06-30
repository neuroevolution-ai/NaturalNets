import numpy as np
import unittest

from naturalnets.environments.app.app import App

# run tests with python -m unittest discover naturalnets/environments/app/tests/

WIDTH = 448
HEIGHT = 448

config = {
    "number_time_steps": 100,
    "screen_width": 448,
    "screen_height": 448,
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