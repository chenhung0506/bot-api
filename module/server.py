# -*- coding: utf-8 -*-
from flask import Flask
# from flask_cors import CORS
import log as logpy
import re
import os
import const
import controller
import flask_restful
import utils
import json
import sys
import test
from flask_restful import Api
from flask_restful import Resource
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

utils.setLogFileName()
log = logpy.logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
controller.setup_route(api)

if __name__=="__main__":
    utils.setLogFileName()
    utils.migrate_db('./migrate/010200001_init.db')
    sched = BackgroundScheduler()
    sched.start()
    sched.add_job(utils.setLogFileName, CronTrigger.from_crontab('59 23 * * *'))
    app.run(host="0.0.0.0", port=const.PORT, debug=True, use_reloader=False)

    # test.migrate_db_test()
    # test.query_bot_work_list_test()
    # test.insert_bot_work_list_test()