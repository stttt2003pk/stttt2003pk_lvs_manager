#!/usr/bin/env python
# -*- coding: utf8 -*-

import os , time

import tornado.auth
import tornado.options
import tornado.web
from tornado.options import define, options

import yaml
import json

#import pymongo
#from pymongo import Connection

from db_model import DB_Model

class LvsAlertApiMessage(tornado.web.RequestHandler):
    @tornado.web.asynchronous

    #get the agent log alert message and insert it to the db
    def post(self):
        message = json.loads(self.request.body)
        handler = DB_Model('LvsAlert')
        result = handler.insertlvsalert(message)
        self.finish()

