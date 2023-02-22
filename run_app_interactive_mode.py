import os

import click
import cv2
import jsonlines
import numpy as np

from naturalnets.environments.gui_app.enums import Color
from naturalnets.environments.i_environment import get_environment_class, IGUIEnvironment
from naturalnets.tools.utils import rescale_values

OUT_DIRECTORY = "out"


def run_interactive(config: dict, save_screenshots: bool, save_state_vector: bool, print_reward: bool):
    def render(action):
        image = app.render_image()

        if save_screenshots:
            cv2.imwrite(os.path.join(OUT_DIRECTORY, "screenshot.png"), image)

        if action is not None:
            # Draw the position of the click as a black circle;
            # thickness=-1 will fill the circle shape with the specified color
            cv2.circle(
                image,
                (action[0], action[1]), radius=4, color=Color.BLACK.value, thickness=-1
            )

        cv2.imshow(window_name, image)

    def click_event(event, x, y, _flags, _params):
        """Sets action when cv2 mouse-callback is detected, i.e. user has clicked."""
        if event == cv2.EVENT_LBUTTONDOWN:
            current_action = np.array([x, y])
            ob, rew, _, info = app.step(rescale_values(current_action,
                                                       previous_low=0,
                                                       previous_high=app.get_screen_size(),
                                                       new_low=-1,
                                                       new_high=1))

            if print_reward:
                print(f"Reward: {rew}")

            if save_state_vector:
                states = []
                for state_info, state in zip(info["states_info"], ob):
                    states.append("({recursion_depth}) {class_name}: ".format(**state_info) + str(state))

                with jsonlines.open(os.path.join(OUT_DIRECTORY, "state_vector.jsonl"), "w") as writer:
                    writer.write_all(states)

            render(action=current_action)

    environment_class = get_environment_class(config["environment"]["type"])
    app = environment_class(config["environment"])

    assert isinstance(app, IGUIEnvironment)

    app.reset(None)

    window_name = app.get_window_name()

    # Create the window here first, so that the callback can be registered
    # The callback simply registers the clicks of a user
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)

    # Create out directory if it does not exist yet (this directory should be added to .gitignore)
    if (save_screenshots or save_state_vector) and not os.path.exists(OUT_DIRECTORY):
        os.makedirs(OUT_DIRECTORY)

    # Render initial GUI view
    render(action=None)

    while True:
        # Waits 50ms for a key press (notice that this does not include mouse clicks,
        # therefore we use the callback method for the clicks)
        key = cv2.waitKey(50)

        # Keycode 27 is the ESC key
        if key == 27:
            cv2.destroyAllWindows()
            break


@click.command()
@click.option("-c", "--config", "config_id", default = 0, type=int, help="Config number (1: GUIApp, else: DummyApp)")
@click.option("-p/-no-p", "--screenshot/--no-screenshot", "save_screenshots",
              default=True, type=bool, help="Save screenshots?")
@click.option("-s/-no-s", "--state/--no-state", "save_state_vector", default=True, type=bool, help="Save state vector?")
@click.option("-r/-no-r", "--reward/--no-reward", "print_reward", default=True, type=bool, help="Print reward?")
def main(config_id: int, save_screenshots: bool, save_state_vector: bool, print_reward: bool):
    if config_id == 0:
        config = {
            "environment": {
                "type": "AnkiApp",
                "number_time_steps": 100,
            }
        }
    elif config_id == 1:
        config = {
            "environment": {
                "type": "GUIApp",
                "number_time_steps": 200,
                "include_fake_bug": False,
                "nearest_widget_click": False,
                "return_clickable_elements": True
            }
        }
    else:
        config = {
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
            }
        }

        save_state_vector = False

    run_interactive(config, save_screenshots, save_state_vector, print_reward)


if __name__ == "__main__":
    main()
