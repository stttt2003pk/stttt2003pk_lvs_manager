#!/usr/bin/env python
# -*- coding: utf8 -*-

from tornado.options import define, options

import os , time

from pymongo import Connection

from setting import *

class mongo_conn():
	def __init__(self):
		self.conn = Connection(options.mongodb,options.mongodb_port)
	def db(self):
		return self.conn[options.db]

####which method call which function
class Model():
	def __init__(self, method):
		self.method = method
#		self.id = id
		self.mongo = mongo_conn()
		self.db = self.mongo.db()
#		self.config = yaml.load(open(options.config))
#		self.agentlist = config['agent']

	def getAccountOne(self,user):
		result = self.db['LvsAccount'].find_one({"username":user})
		return result

	def getAccountPass(self, passwd):
		result = self.db['LvsAccount'].find_one({"passwd":passwd})
		return result

