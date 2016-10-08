import json


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


class Api:
    def __init__(self, name):
        self.name = name
        self.accounts = []
        self.totalCalls = 0
        self.callsWithResponseCount = 0
        self.success = 0
        self.failure = 0
        self.totalResponseTime = 0
        self.avgResponseTime = 0
        self.failureMessage = {}

    def serialize(self):
        return {
            'name': self.name,
            'totalCalls': self.totalCalls,
            'callsWithResponseCount': self.callsWithResponseCount,
            'success': self.success,
            'failure': self.failure,
            'avgResponseTime': self.avgResponseTime,
            'failureMessages': json.dumps(self.failureMessage)
        }
