import datetime
import json
import time

from bson import json_util
from insidelogs import mongo
from insidelogs.models.Account import Account
from insidelogs.models.AccountLog import AccountLog
from insidelogs.models.Api import Api
from insidelogs.models.LogKey import LogKey
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


db = mongo['ssprod']


def process(self, params):
    logger.info("Start task")
    resultMap = {}
    getDataApiWise(params, resultMap)
    for key, value in resultMap.items():
        res = value.totalResponseTime
        call = value.callsWithResponseCount
        if res is not None and call is not None and call is not 0:
            temp = resultMap.get(key)
            temp.avgResponseTime = res / call
            resultMap.update({key: temp})
    return resultMap


def getDataApiWise(params, resultMap):
    fromDate = params.get('fromDate')
    toDate = params.get('toDate')
    apiPicked = params.get('apiPicked')
    cursor = commonGetData(fromDate, toDate, apiPicked)
    json_results = []
    for item in cursor:
        json_results.append(item)
        processResults(item, resultMap)


def commonGetData(fromDate, toDate, apiPicked):
    logger = db['logger_log_' + str(time.strftime("%d-%m-%Y"))]
    if fromDate is None and toDate is None:
        todayTime = time.strftime("%d-%m-%Y")
        epoch = int(time.mktime(time.strptime(todayTime, "%d-%m-%Y")))
        epoch *= 1000
        currentHour = datetime.datetime.now().hour
        fromDate = int(epoch) + int(int(currentHour - 1) * 3600000)
        toDate = int(epoch) + int(int(currentHour) * 3600000)
    if apiPicked is None:
        cursor = logger.find({"timeStamp": {"$gt": fromDate, "$lt": toDate}})
    else:
        cursor = logger.find({"timeStamp": {"$gt": fromDate, "$lt": toDate}, "api": {"$in": apiPicked}})
    cursor.batch_size(1000)
    return cursor


def toJson(data):
    """Convert Mongo object(s) to JSON"""
    return json.dumps(data, default=json_util.default)


def processResults(r, rmap):
    if rmap.get(r.get(LogKey.API.value)) is not None:
        api = rmap.get(r.get(LogKey.API.value))
        if r.get(LogKey.ACCOUNT.value) is not None:
            api.accounts.append(r.get(LogKey.ACCOUNT.value))
        api.totalCalls += 1
        if r.get(LogKey.HAS_ENCOUNTERED_EXCEPTION.value):
            api.failure += 1
            if r.get(LogKey.ERROR_MESSAGE.value) is not None:
                if r.get(LogKey.ERROR_MESSAGE.value).replace(".", " ") not in rmap.get(
                        r.get(LogKey.API.value)).failureMessage:
                    rmap.get(r.get(LogKey.API.value)).failureMessage.update(
                        {r.get(LogKey.ERROR_MESSAGE.value).replace(".", " "): 0})
                else:
                    rmap.get(r.get(LogKey.API.value)).failureMessage.get(
                        r.get(LogKey.ERROR_MESSAGE.value).replace(".", " "))
                    rmap.get(r.get(LogKey.API.value)).failureMessage[
                        r.get(LogKey.ERROR_MESSAGE.value).replace(".", " ")] += 1

        else:
            api.success += 1
            if r.get(LogKey.RESPONSE_TIME.value) is not None:
                api.totalResponseTime += r.get(LogKey.RESPONSE_TIME.value)
                api.callsWithResponseCount += 1
    else:
        if r.get(LogKey.API.value) is None:
            rmap.update({r.get(LogKey.MODULE.value): Api(r.get(LogKey.MODULE.value))})
        else:
            rmap.update({r.get(LogKey.API.value): Api(r.get(LogKey.API.value))})


def toEpoch(date):
    date_time = date
    pattern = '%Y/%m/%d %H:%M:%S'
    return int(time.mktime(time.strptime(date_time, pattern)) * 1000)


def processResultsForAccountWise(item, resultMap):
    if item.get(LogKey.ACCOUNT.value) is None:
        return
    if resultMap.get(item.get(LogKey.ACCOUNT.value)) is not None:
        account = resultMap.get(item.get(LogKey.ACCOUNT.value))
    else:
        resultMap.update({item.get(LogKey.ACCOUNT.value): Account(item.get(LogKey.ACCOUNT.value))})
        account = resultMap.get(item.get(LogKey.ACCOUNT.value))
    addApiTOAccountIfNotExist(account, item)


def processDataForAccountApi(account, item, apiName):
    newApi = account.api.get(apiName)
    newApi.totalCalls += 1
    if item.get(LogKey.HAS_ENCOUNTERED_EXCEPTION.value) is False:
        newApi.success += 1
        if item.get(LogKey.RESPONSE_TIME.value) is not None:
            newApi.totalResponseTime += item.get(LogKey.RESPONSE_TIME.value)
            newApi.callsWithResponseCount += 1
    else:
        newApi.failure += 1
        if item.get(LogKey.ERROR_MESSAGE.value) is not None:
            if item.get(LogKey.ERROR_MESSAGE.value).replace(".", " ") not in newApi.failureMessage:
                newApi.failureMessage.update({item.get(LogKey.ERROR_MESSAGE.value).replace(".", " "): 0})
            else:
                newApi.failureMessage.get(item.get(LogKey.ERROR_MESSAGE.value).replace(".", " "))
                newApi.failureMessage[item.get(LogKey.ERROR_MESSAGE.value).replace(".", " ")] += 1
    account.api[apiName] = newApi


def addApiTOAccountIfNotExist(account, item):
    apiName = getApiName(item)
    if account.api.get(apiName) is None:
        account.api.update({apiName: Api(apiName)})
    processDataForAccountApi(account, item, apiName)


def getDataAccountWise(fromDate, toDate, apiPicked, hour):
    cursor = commonGetData(fromDate, toDate, apiPicked)
    json_results = []
    result_map = {}
    serializeList = []
    for item in cursor:
        json_results.append(item)
        processResultsForAccountWise(item, result_map)
    if result_map is not None:
        for key, value in result_map.items():
            del serializeList[:]
            p = list(value.api.values())
            for v in p:
                if v.callsWithResponseCount != 0:
                    v.avgResponseTime = v.totalResponseTime / v.callsWithResponseCount
                serializeList.append(v.serialize())
            temp = list(serializeList)
            result_map[key] = temp
    saveDataAccountWise(result_map)
    return result_map


def getApiName(item):
    if item.get(LogKey.API.value) is not None:
        return item.get(LogKey.API.value)
    else:
        return item.get(LogKey.SERVICE.value)


def convertData(data):
    convertedList = []
    now = datetime.datetime.now()
    for k, v in data.items():
        newAccountLog = AccountLog(k)
        newAccountLog.timeOfSave = now.ctime()
        newAccountLog.hourNumber = now.hour % 24
        newAccountLog.api = v
        convertedList.append(newAccountLog.dict())
    return convertedList


def saveDataAccountWise(data):
    account_log = db['account_logs']
    if data is not None:
        try:
            converted_list = convertData(data)
        except Exception as e:
            raise e
    account_log.insert_many(converted_list)
