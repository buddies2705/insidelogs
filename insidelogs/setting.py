from datetime import timedelta
# minute=25, hour='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'add-every-minute': {
        'task': 'tasks.accountWiseLogResultsTask',
        'schedule': crontab()
    },
}
CELERY_TIMEZONE = 'Asia/Calcutta'
SECRET_KEY = 'not_a_secret'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
MONGO_HOST = 'Enter Host'
MONGO_DBNAME = 'Enter DB Name'
