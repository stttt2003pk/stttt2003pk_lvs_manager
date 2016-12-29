#!/usr/bin/env python
# -*- coding: utf8 -*-

from tornado.options import define, options

import os , time

from pymongo import Connection

from setting import *

import json

class mongo_conn():
	def __init__(self):
		self.conn = Connection(options.mongodb,options.mongodb_port)
	def db(self):
		return self.conn[options.db]

####which method call which function
class DB_Model():
	def __init__(self, method):
		self.method = method
#		self.id = id
		self.mongo = mongo_conn()
		self.db = self.mongo.db()
#		self.config = yaml.load(open(options.config))
#		self.agentlist = config['agent']

	def getAccountOne(self,user):
		result = self.db['LvsAccount'].find_one({"user":user})
		return result


####test DB_Model
#handler = DB_Model('test account')
#print handler.getAccountOne('admin')


