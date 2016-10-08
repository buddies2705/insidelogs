from flask import Flask
from pymongo import MongoClient

from insidelogs import setting

app = Flask(__name__)
app.config.from_object(setting)
mongo = MongoClient(host='Enter Host')

import insidelogs.views.views
