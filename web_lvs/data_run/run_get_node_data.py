#!/usr/bin/python
# -*- coding: utf8 -*-

import os,sys,logging

from pymongo import MongoClient

import yaml

import time
import datetime

import urllib2

cur_dir = os.path.dirname(os.path.abspath(__file__))

settings = {
                'config': os.path.join(cur_dir,"config.yaml"),
                'logfile': os.path.join(cur_dir,"log","system.log"),
                'mongodb': 'localhost',
                'mongodb_port': 27017,
                'db': 'Lvs_stttt2003pk_manager',
}

try:
    logging.basicConfig(
        level=logging.NOTSET,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=settings['logfile'],
        filemode='a'
    )
    logging = logging.getLogger()
except Exception as err:
    print("Error: %s %s" %(err, settings['logfile']))
    sys.exit(2)

class MongoSession():
    def __init__(self):
        self.conn = MongoClient(settings['mongodb'],settings['mongodb_port'])
        self.db = self.conn[settings['db']]

    def close(self):
        try:
            self.conn.end_request()
            self.conn.close()
            logging.info('close mongo connection Success !')
        except Exception, e:
            logging.warning('close mongo connection fail !')

    def insert(self, id, data_type, data):
        _time = time.time()
        collection = self.db[data_type]
        insert_data = {
            "id":id,
            "time":_time,
            "data": data
        }
        try:
            _id = collection.insert(insert_data):
            self.conn.end_request()
            logging.info('Insert data (ID:%s) Success !' % id) 
            return id
        except Exception, e:
            return e

    def insert_demo(self, data_type,insert_data)
        _time = time.time()
        collection =self.db[data_type]
        try:
            _id = collection.insert(insert_data)
            self.conn.end_request()
            logging.info('Method: Insert | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            return e

    def upsert(self,data_type,find,update):
        collection = self.db[data_type]
        try:
            _id = collection.update(find,update,True)
            self.conn.end_request()
            logging.info('Method: Upsert | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            logging.warning('Method: Upsert | table: %s | result: %s' % (data_type,e))

    def update(self,data_type,find,update):
        collection = self.db[data_type]
        try:
            _id = collection.update(find,update)
            self.conn.end_request()
            logging.info('Method: Update | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            logging.warning('Method: Update | table: %s | result: %s' % (data_type,e))

    def find_one(self,data_type,find):
        collection = self.db[data_type]
        try:
            _id = collection.find_one(find)
            self.conn.end_request()
            logging.info('Method: FindOne | table: %s | result: Success ' % (data_type))
        except Exception, e:
            logging.warning('Method: FindOne | table: %s | result: %s' % (data_type,e))


class get_Lvs_Node_Data(object):
    def __init__(self):
        pass
        
    def getmonitordata(self, agent,port,data_type):
        url = "http://%s:%s/node/%s/" %(agent, port, data_type)
        fail = 0
        retry =5

        while True:
            try:
                if fail > retry:
                    logging.warning('Get Monitor Data Failed | %s' % url)
                    return None
                res = urllib2.urlopen(url, timeout=2)
                return json.loads(res.read())
            except Exception, e:
                fails += 1
            else:
                logging.info('Get Monitor Data Success | %s ' % url)
                break

    def getlvstrffic(self, agent_ip, port):
        url = 'http://%s:%s/node/GetLvsTraffic/' % (agent_ip,port)
        fails = 0
        retry = 5
        while True:
            try:
                if fail > retry:
                    logging.warning('Get Monitor Data Failed | %s' % url)
                    return None
                res = urllib2.urlopen(url, timeout=2)
                return json.loads(res.read())
            except Exception, e:
                fails += 1 
            else:
                logging.info('Get Monitor Data Success | %s ' % url)
                break

    def lvstraffic_handler(self, id,agent_ip,agent_port,cluster,_time):
        mongo_task = MongoSession()
        sum_dict = {}
        inpkts_sum = 0
        outpkts_sum = 0
        inbytes_sum = 0
        outbytes_sum = 0
        conns_sum = 0

        data = self.getlvstrffic(agent_ip,agent_port)
        for vip_dict in data:
            vip_dict["id"] = id
            vip_dict["time"] = _time
            inpkts_sum += vip_dict['inpkts_sum_per']
            outpkts_sum += vip_dict['outpkts_sum_per']
            inbytes_sum += vip_dict['inbytes_sum_per']
            outbytes_sum += vip_dict['outbytes_sum_per']
            conns_sum += vip_dict['conns_sum_per']
            vip_dict["cluster"] = cluster

            result = mongo_task.insert_demo('GetLvsTraffic_demo',vip_dict)
            find = {
                "cluster":cluster,
                "time":_time,
                "vip":vip_dict["vip"]
            }
            update = {
                        "$inc":
                                {
                                    "inpkts_sum_per":vip_dict["inpkts_sum_per"],
                                    "outpkts_sum_per":vip_dict["outpkts_sum_per"],
                                    "inbytes_sum_per":vip_dict["inbytes_sum_per"],
                                    "outbytes_sum_per":vip_dict["outbytes_sum_per"],
                                    "conns_sum_per":vip_dict["conns_sum_per"],
                                }
            }
            mongo_task.upsert('GetLvsTraffic_cluster',find,update)

        sum_dict["inpkts_sum"] = inpkts_sum
        sum_dict["outpkts_sum"] = outpkts_sum
        sum_dict["inbytes_sum"] = inbytes_sum
        sum_dict["outbytes_sum"] = outbytes_sum
        sum_dict["conns_sum"] = conns_sum
        sum_dict["time"] = _time
        sum_dict["id"] = id
        sum_dict["cluster"] = cluster

        mongo_task.insert_demo('GetLvsTraffic_sum',sum_dict)
        find = {"cluster":cluster,"time":_time}
        update = {
                    "$inc": 
                            {
                                "inpkts_sum":inpkts_sum ,
                                "outpkts_sum":outpkts_sum,
                                "inbytes_sum":inbytes_sum,
                                "outbytes_sum":outbytes_sum,
                                "conns_sum":conns_sum
                            }
        }
        mongo_task.upsert('GetLvsTraffic_cluster_sum',find,update)
        mongo_task.close()
        return None

































































 
                    



























































