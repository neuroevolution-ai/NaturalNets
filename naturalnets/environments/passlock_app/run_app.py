from naturalnets.environments.passlock_app.passlock_app import PasslockApp

WIDTH = 1100
HEIGHT = 850

config = {
    "type": "PasslockApp",
    "number_time_steps": 100,
    "include_fake_bug": False
}

if __name__ == "__main__":

    app = PasslockApp(config)
    app.reset()
    app.interactive_mode()
    