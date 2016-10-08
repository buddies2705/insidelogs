import time


class AccountLog:
    def __init__(self, account):
        self.account = account
        self.hourNumber = 0
        self.timeOfSave = 0
        self.date = time.strftime("%d/%m/%Y")
        self.type = 'ACCOUNT_WISE'
        self.api = []

    def dict(self):
        temp = self.__dict__
        temp.update({'id': str(temp.get('date')) + str(temp.get('hourNumber')) + str(temp.get('account'))})
        return temp
