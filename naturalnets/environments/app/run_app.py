from naturalnets.environments.app.app import GUIApp

WIDTH = 448
HEIGHT = 448

config = {
    "type": "GUIApp",
    "number_time_steps": 100,
    "screen_width": 448,
    "screen_height": 448
}

if __name__ == "__main__":

    app = GUIApp(config)
    app.interactive_mode()
