from random import randrange
import time
import numpy as np

from naturalnets.environments.app.app import App

# run tests with python -m unittest discover naturalnets/environments/app/tests/

WIDTH = 448
HEIGHT = 448

config = {
    "number_time_steps": 10**6,
    "screen_width": 448,
    "screen_height": 448,
	"interactive": False,
    "monkey_tester": True
}

if __name__ == "__main__":

    app = App(config)
    time_sum = 0
    action = None
    for i in range(config["number_time_steps"]):
        #app.render(action)
        action = np.array([randrange(0,448), randrange(0,448), 0, 0],dtype=int)

        t0 = time.time()
        app.step(action)
        t1 = time.time()
        time_sum += (t1-t0)

        if i % 10**5 == 0:
            print("{} steps done.".format(i*10**5))

    print(time_sum/config["number_time_steps"])
    