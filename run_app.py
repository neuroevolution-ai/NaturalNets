import jsonlines
import os
import cv2
import numpy as np
from naturalnets.environments.gui_app.gui_app import GUIApp
from naturalnets.environments.gui_app.enums import Color
from naturalnets.tools.utils import rescale_values

WIDTH = 448
HEIGHT = 448

config = {
    "type": "GUIApp",
    "number_time_steps": 100,
    "include_fake_bug": False
}

print_reward = True
save_screenshots = True
save_state_vector = True


def render(action):
    image = app._render_image()

    if save_screenshots:
        cv2.imwrite(os.path.join('out', 'screenshot.png'), image)

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
        ob, rew, _, info = app.step(rescale_values(current_action, previous_low=0, previous_high=447, new_low=-1,
                                                   new_high=1))

        if print_reward:
            print(f"Reward: {rew}")

        if save_state_vector:
            states = []
            for state_info, state in zip(info['states_info'], ob):
                states.append(str(state_info) + " " + str(state))

            with jsonlines.open(os.path.join('out', 'state_vector.jsonl'), 'w') as writer:
                writer.write_all(states)

        render(current_action)


if __name__ == "__main__":

    app = GUIApp(config)
    app.reset()
    window_name = app.get_window_name()

    # Create the window here first, so that the callback can be registered
    # The callback simply registers the clicks of a user
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)

    # Create out directory if it does not exist yet (this directory should be added to .gitignore)
    if (save_screenshots or save_state_vector) and not os.path.exists('out'):
        os.makedirs('out')

    # Render initial GUI view
    render(None)

    while True:
        # Waits 50ms for a key press (notice that this does not include mouse clicks,
        # therefore we use the callback method for the clicks)
        key = cv2.waitKey(50)

        # Keycode 27 is the ESC key
        if key == 27:
            cv2.destroyAllWindows()
            break
