from typing import List
from naturalnets.environments.password_manager_app.account_manager.account import Account
from naturalnets.environments.password_manager_app.constants import NAME_ONE, NAME_THREE, NAME_TWO


class AccountManager:
    
    currentAccounts: List[Account] = []

    @staticmethod
    def add_account(account: Account):
        if len(AccountManager.currentAccounts) < 3:
            if not AccountManager.is_in_current_accounts(account.get_account_name()):
                AccountManager.currentAccounts.append(account)
                AccountManager.return_to_main_page()
            else:
                AccountManager.error(account.get_account_name())


    @staticmethod
    def edit_account(account: Account, old_account: Account):
        AccountManager.delete_account(old_account.get_account_name())
        AccountManager.add_account(account)

    @staticmethod
    def delete_account(account_name: str):
        for current_account in AccountManager.currentAccounts:
            if current_account.get_account_name() == account_name:
                AccountManager.currentAccounts.remove(current_account)

    @staticmethod
    def get_account_by_name(account_name: str):
        for current_account in AccountManager.currentAccounts:
            if current_account.get_account_name() == account_name:
                return current_account
        return None

    @staticmethod
    def is_in_current_accounts(account_name: str):
        if AccountManager.currentAccounts is None:
            return False
        for currentAccount in AccountManager.currentAccounts:
            if account_name == currentAccount.get_account_name():
                return True
        return False
    
    @staticmethod
    def current_state():
        if (AccountManager.currentAccounts is None):
            return [0, 0]
        len_current_accounts = len(AccountManager.currentAccounts)

        if (len_current_accounts == 0):
            return [0, 0]
        elif (len_current_accounts == 3):
            return [7, 0]
        elif (len_current_accounts == 1):
            name = AccountManager.currentAccounts[0].get_account_name()
            if name == NAME_ONE:
                return [1, 1]
            elif name == NAME_TWO:
                return [2, 1]
            else:
                return [3, 1]
        elif (len_current_accounts == 2):
            name = AccountManager.currentAccounts[0].get_account_name()
            if name == NAME_ONE:
                if AccountManager.currentAccounts[1].get_account_name() == NAME_TWO:
                    return [4, 0]
                else:
                    return [5, 0]
            elif name == NAME_TWO:
                if AccountManager.currentAccounts[1].get_account_name() == NAME_ONE:
                    return [4, 0]
                else:
                    return [6, 0]
            else:
                if AccountManager.currentAccounts[1].get_account_name() == NAME_ONE:
                    return [5, 0]
                else:
                    return [6, 0]
                
    def error(account_name: str):
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.function_account_error(account_name)

    def return_to_main_page():
        from naturalnets.environments.password_manager_app.app_controller import AppController

        AppController.main_window.set_current_page(None)
    

