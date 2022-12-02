from naturalnets.environments.gui_app.gui_app import GUIApp

WIDTH = 448
HEIGHT = 448

config = {
    "type": "GUIApp",
    "number_time_steps": 100,
    "include_fake_bug": False
}

if __name__ == "__main__":

    app = GUIApp(config)
    app.reset()
    app.interactive_mode(save_screenshots=True, save_state_vector=True)
    