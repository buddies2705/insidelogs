from flask import jsonify
from flask import request, render_template, redirect
from insidelogs import app
from insidelogs.service.helper import process, toEpoch, getDataAccountWise

apiList = ["Enter Api List"]


@app.route("/")
def main():
    return redirect("/api")


@app.route("/api", methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('input.html')
    if request.method == 'POST':
        inputData = request.form
        params = {}
        fromDate = toEpoch(inputData.get('fromDate') + ' 00:00:00')
        toDate = toEpoch(inputData.get('toDate') + ' 00:00:00')
        params.update({'fromDate': fromDate})
        params.update({'toDate': toDate})
        params.update({'isScheduler': False})
        resultMap = process(params)
        list_of_values = list(resultMap.values())
        p = []
        for a in list_of_values:
            p.append(a.serialize())
        return jsonify(p)


@app.route("/account", methods=['GET', 'POST'])
def accountWiseData():
    if request.method == 'GET':
        return render_template('account.html', apiList=apiList)
    if request.method == 'POST':
        inputData = request.form
        fromDate = toEpoch(inputData.get('fromDate') + ' 00:00:00')
        toDate = toEpoch(inputData.get('toDate') + ' 00:00:00')
        apiPicked = inputData.getlist('api_picks')
        hour = inputData.get('hours')
    result = getDataAccountWise(fromDate, toDate, apiPicked, hour)
    return jsonify(result)




#
# @app.route('/status/<task_id>')
# def taskstatus(task_id):
#     task = apitask.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         # job did not start yet
#         response = {
#             'state': task.state,
#             'current': 0,
#             'total': 1,
#             'status': 'Pending...'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'current': task.info.get('current', 0),
#             'total': task.info.get('total', 1),
#             'status': task.info.get('status', '')
#         }
#         if 'result' in task.info:
#             response['result'] = task.info['result']
#     else:
#         # something went wrong in the background job
#         response = {
#             'state': task.state,
#             'current': 1,
#             'total': 1,
#             'status': str(task.info),  # this is the exception raised
#         }
#     return jsonify(response)
