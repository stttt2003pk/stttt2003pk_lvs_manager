#!/usr/bin/env python
# -*- coding: utf8 -*-

from tornado.options import define, options

import os , time

from pymongo import Connection

from setting import *

import json
from bson.objectid import ObjectId

class mongo_conn():
	def __init__(self):
		self.conn = Connection(options.mongodb,options.mongodb_port)
	def db(self):
		return self.conn[options.db]

####which method call which function
class DB_Model():
    def __init__(self, method):                                                               
        self.method = method                                                                  
#       self.id = id 
        self.mongo = mongo_conn()                                                             
        self.db = self.mongo.db()
#       self.config = yaml.load(open(options.config))                                         
#       self.agentlist = config['agent']                                                      
    
    def getAccountOne(self,user):
        result = self.db['LvsAccount'].find_one({"user":user})
        return result
                                                                                              
    def insertLvsManagerConfigVipInstance(self, data):
        self.db['LvsManagerConfig'].insert(data, manipulate=False)
        return True    

    def getLvsManagerConfigVipInstanceList(self, id):
        result = self.db['LvsManagerConfig'].find({"cluster_id" : id})
        return list(result) 

    def getLvsManagerConfigVipInstanceInfo(self, id):
        result = self.db['LvsManagerConfig'].find_one({"_id" : ObjectId(id)})
        return result

    def UpdateLvsManagerConfigVipInstance(self, id, data):
        result = self.db['LvsManagerConfig'].update({"_id": ObjectId(id)}, data)

    def UpdateLvsManagerConfigVipInstanceToOffline(self, id):
        result = self.db['LvsManagerConfig'].update({"_id": ObjectId(id)},{"$set": {"status":"offline"}})

    def UpdateLvsManagerConfigVipInstanceToOnline(self, id):
        result = self.db['LvsManagerConfig'].update({"_id": ObjectId(id)},{"$set": {"status":"online"}})

    def DelLvsManagerConfigVipInstance(self, id):
        result = self.db['LvsManagerConfig'].remove({"_id": ObjectId(id)})

    def getLvsManagerPublishLastRev(self, id):
        result = self.db['LvsManagerPublish'].find({"cluster_id": id}).sort("time", -1)
        if result.count() != 0:
            return list(result)[0]
        else:
            return False

    def insertLvsManagerPublish(self, data):
        result = self.db['LvsManagerPublish'].insert(data)
        return str(result)

    def updateLvsManagerPublishResult(self, id, publishresult):
        self.db['LvsManagerPublish'].update({"_id": ObjectId(id)},{"$set": { "publish_result" : publishresult }})
        return True

    def getLvsManagerPublishList(self, id):
        result = self.db['LvsManagerPublish'].find({"cluster_id": id}).sort("time", -1)
        return list(result)

    def getLvsManagerPublishOne(self, id):
        result = self.db['LvsManagerPublish'].find_one({"_id": ObjectId(id)})
        return result

    def removeLvsManagerConifghForCluster(self, id):
        self.db['LvsManagerConfig'].remove({"cluster_id": id})
        return True

    def insertlvsalert(self, message):
        result = self.db['LvsAlert'].insert(message)
        return result

####test DB_Model
#handler = DB_Model('test account')
#print handler.getAccountOne('admin')


