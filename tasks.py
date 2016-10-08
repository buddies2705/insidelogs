from insidelogs import app
from insidelogs.service.helper import getDataAccountWise
from mcelery import make_celery

celery = make_celery(app)


@celery.task()
def accountWiseLogResultsTask():
    getDataAccountWise(None, None, None, None)
