class PageManager:
    @staticmethod
    def return_to_main_page() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)

    @staticmethod
    def error(account_name: str) -> None:
        "This opens the error page. Gets thrown when the username already exists."
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_account_error(account_name)

    @staticmethod
    def open_about() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(AppController.main_window.about)

    @staticmethod
    def open_file_system() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(AppController.main_window.file_system)

    @staticmethod
    def open_master_password() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(AppController.main_window.master_password)

    @staticmethod
    def add_account() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_add_account()

    @staticmethod
    def delete_account() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_delete_account()

    @staticmethod
    def edit_account() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_edit_account()

    @staticmethod
    def view_account() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_view_account()

    @staticmethod
    def copy_username() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.copy_username()
        AppController.main_window.set_current_page(None)

    @staticmethod
    def copy_password() -> None:
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.copy_password()
        AppController.main_window.set_current_page(None)
