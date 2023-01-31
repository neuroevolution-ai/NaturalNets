from typing import List
from naturalnets.environments.password_manager_app.account_manager.account import Account


class AccountManager:
    
    currentAccounts: List[Account] = []

    @staticmethod
    def addAccount(account: Account):
        if len(AccountManager.currentAccounts) < 3:
            if account not in AccountManager.currentAccounts:
                AccountManager.currentAccounts = AccountManager.currentAccounts.__add__(account)


    @staticmethod
    def deleteAccount(account_name: str):
        for account in AccountManager.currentAccounts:
            if account.getAccountName() == account_name:
                AccountManager.currentAccounts.remove(account)
