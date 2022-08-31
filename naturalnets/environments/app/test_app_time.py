from random import randrange
import time
import numpy as np

from naturalnets.environments.app.app import GUIApp

WIDTH = 448
HEIGHT = 448

config = {
    "type": "GUIApp",
    "number_time_steps": 10**6,
    "screen_width": 448,
    "screen_height": 448,
    "interactive": False,
    "monkey_tester": True
}

state_diff: np.array = None


def calc_state_diff(curr_state, init_state, target):
    diff = np.bitwise_xor(curr_state, init_state)
    target = np.bitwise_or(diff, target)
    return target


if __name__ == "__main__":

    app = GUIApp(config)
    time_sum = 0
    action = None
    initial_state = np.copy(app.get_state())
    state_diff = np.zeros(len(initial_state), dtype=int)
    for i in range(config["number_time_steps"]):
        # app.render(action)
        action = np.array([randrange(0, 448), randrange(0, 448), 0, 0], dtype=int)

        t0 = time.time()
        app.step(action)
        t1 = time.time()
        time_sum += (t1-t0)

        if i % 10**5 == 0:
            print(f"{i} steps done.")

        state_diff = calc_state_diff(app.get_state(), initial_state, state_diff)

    print(f"Time per timestep: {time_sum/config['number_time_steps']}")
    print(f"State diff: {state_diff}")
    print(f"Changed state elements: {np.sum(state_diff)/len(state_diff)}%")
