#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options
import tornado.web
from tornado.escape import json_decode, json_encode

import pymongo
from pymongo import Connection

from db_model import DB_Model
from bytesformat import bytes2human

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import json
import urllib

import time
import datetime

import logging 
from tornado.log import access_log, app_log, gen_log

import yaml
import codecs

####real server alived html
def rs_is_lived(weight):
	if int(weight) == 0:
		return False
	else:
		return True

####manager admin acount
def user_is_manager(user):
	handler = DB_Model('LvsAccount')
	user_info = handler.getAccountOne(user)
	if user_info['is_manager'] or user_info['super_manager']:
		return True
	else:
		return False

####bytes format filter,use a google filter,Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
def bytesformat(bytes):
	return bytes2human(bytes)

####real server str split
def format_rs_str(rs):
	_rs = rs.split(':')
	return _rs[0]

####timestamp UTC to human
def timestamptodate(timestamp):
	return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

cur_dir = os.path.dirname(os.path.abspath(__file__))
####for rendering templates
class TemplateRendering():
	def __init__(self):
	#	self.settings = dict(
    #        template_path = os.path.join(cur_dir,'templates/'),
    #        static_path = os.path.join(cur_dir,'lib/'),
    #        cookie_secret = "SunRunVas38288446TestStttt2003pk",
    #        login_url = "/",
    #    )
		pass

	def render_template(self, template_name, **kwargs):
		template_dirs = []

		#print self.settings.get('template_path', '666666666')
		if self.settings.get('template_path', ''):
			template_dirs.append(self.settings["template_path"])
			#print template_dirs

		####jinja2 env setting,setthen test and fileter
		env = Environment(loader=FileSystemLoader(template_dirs))
		env.tests['rs_is_lived'] = rs_is_lived
		env.tests['user_is_manager'] = user_is_manager
		env.filters['timestamptodate'] = timestamptodate
		env.filters['bytesformat'] = bytesformat
		env.filters['format_rs_str'] = format_rs_str

		try:
			template = env.get_template(template_name)
		except TemplateNotFound:
			raise TemplateNotFound(template_name)

		content = template.render(kwargs)
		
		return content

####basehendler rendering overwrite
class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
	####render2 method
	def render2(self, template_name, **kwargs):

		kwargs.update({
			'settings': self.settings,
			'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
			'request': self.request,

			'xsrf_token': self.xsrf_token,
			'xsrf_form_html': self.xsrf_form_html,
            #{{ current_user }}
			'current_user':self.get_current_user(),
			
		})

		content = self.render_template(template_name, **kwargs)
		self.write(content)

	def template(self, template_name, **kwargs):
		
		kwargs.update({
			'settings': self.settings,
			'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),

			'request': self.request,

			'xsrf_token': self.xsrf_token,
			'xsrf_form_html': self.xsrf_form_html,
		})
		
		content = self.render_template(template_name, **kwargs)
		return content

	####overwrite tornado.web.RequestHandler get user method
	def get_current_user(self):
		
		user_id = self.get_secure_cookie("user")
		if not user_id:
			return None

		return user_id

	def get_context(self):

		self.context = {'current_user': self.get_current_user()}
		return self.context

####home
class HomeHandler(BaseHandler):
	def get(self):
		'''		
		index
		'''
		current_user = self.get_current_user()
		if current_user:
			self.redirect('/charts/')
		else:
			lvs_url = options.lvs_url
			'''
			redirect uri
			'''
			ret = "%slogin" %lvs_url
			self.redirect(ret)

###user logout
class Loginout(BaseHandler):
	def get(self):
		lvs_url = options.lvs_url	
		ret = "%slogout?forward=%s" % (lvs_url, lvs_url)
		self.redirect(ret)

####login_auth
class LoginAuth(BaseHandler):
	def post(self):

		login_name_true = None
		login_pass_true = None
		####from ajax

		post_data = json_decode(self.request.body)

		login_name_auth = post_data.get('user', True)
		login_pass_auth = post_data.get('passwd', True)
		
		####from db
		handler = DB_Model('Account')
		result  = handler.getAccountOne(login_name_auth)

		if result:
			login_name_true = result.get("user", False)
			login_pass_true = result.get("passwd", False) 

			if login_name_auth == login_name_true and login_pass_auth == login_pass_true:
				self.write('ok')
				time_now = timestamptodate(time.time())
				if login_name_true != 'admin':
					user_data = {"username":login_name_true, "is_manager":False, "is_super_manager":False, "login_time":time_now}
					self.set_secure_cookie("user", login_name_true, expires_days=options.cookies_expires)
			else:
				self.write('username or password not match')
		else:
			self.write('username or password not match')

####login_html
class Login(BaseHandler):
	def get(self):
		self.render2('login.html')

####charts
class ChartsHandler(BaseHandler):
	def get(self):
		self.render2('charts.html')

def search_agent(id):
	config = yaml.load(open(options.config))
	agent_list = config['agent']
	for i in agent_list:
		if id == i['id']:
			return i

	return None

def search_cluster(id):
	config = yaml.load(open(options.config))
	cluster_list = config['cluster']
	for i in cluster_list:
		if id == i['id']:
			return i
	
	return None


####cluster list
class LvsManager(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        cluster_list = []

        config = yaml.load(open(options.config))

        current_user = self.get_current_user()
        handler = DB_Model('account')
        result = handler.getAccountOne(current_user)

        if result["super_manager"]:
            cluster_list = config['cluster']
        elif result["is_manager"]:
            for name in config['cluster']:
                if current_user in name['manager_user']:
                    cluster_list.append(name)
        else:
            pass

        for cluster in cluster_list:
            lb_list = []
            for lb in cluster['agent']:
                lb_info = search_agent(lb)
                lb_list.append({
                                "id":lb_info['id'],
                                "ipadd":lb_info['ipadd'],
                                "port":lb_info['port'],
                                
                                })
            cluster['lb'] = lb_list

        self.render2('lvsmanager.html',cluster_list=cluster_list)
        #self.write(cluster_list[0])

#add vip instance
class lvsManagerDeployAdd(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None) 
        self.render2('lvsmanager_deploy_add.html', cluster=id)

    #from post, set the addition information to the mongo
    def post(self):
        
        data = json.loads(self.request.body)
        
        data['status'] = 'online'
        data['mailto'] = data['mailto'].split(',')

        vip_group = data['vip_group'].split(',')
        vip_group_list = []
        
        for vip in vip_group:
            vip_port = vip.split(':')
            vip_group_list.append({"vip" : vip_port[0],
                                    "port" : vip_port[1]
                                })

        data['vip_group'] = vip_group_list

        for rs in data['rs']:
            rs['port'] = rs['port'].split(',')
        #this methon will change the data ram, add "_id" as an object, an can't be translate to json and can't be write in tornado,if manipulate = True
        handler = DB_Model('LvsManagerConfig')
        handler.insertLvsManagerConfigVipInstance(data)

        self.write(data)

#get vip instances from db of this cluster_id
class LvsManagerDeploy(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        id = self.get_argument('id', None)
        
        #get the config from db, return a mongo cursor
        handler = DB_Model('LvsManagerConfig')
        vipinstanceinfo = handler.getLvsManagerConfigVipInstanceList(id)
        self.render2('lvsmanager_deploy.html', vipinstanceinfo=vipinstanceinfo, cluster=id)

#edit the configuration(vip instance)
class LvsManagerDeployEdit(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        id = self.get_argument("id",None)
        handler = DB_Model('LvsManagerConfig')
        vipinstanceinfo = handler.getLvsManagerConfigVipInstanceInfo(id)
        
        vipinstanceinfo['mailto'] = ','.join(vipinstanceinfo['mailto'])
        vipgroup = vipinstanceinfo['vip_group']

        vipgrouplist = []
        for vip in vipgroup:
            vipgrouplist.append("%s:%s" %(vip['vip'],vip['port']))

        vipinstanceinfo['vip_group'] = ','.join(vipgrouplist) 

        for i,rs in enumerate(vipinstanceinfo['rs']):
            rs['i'] = i
            rs['port'] = ','.join(rs['port'])

        self.render2('lvsmanager_deploy_edit.html', vipinstance=vipinstanceinfo, cluster=id)

    def post(self):
        id = self.get_argument("id",None)
        data = json.loads(self.request.body)
        data['mailto'] = data['mailto'].split(',')
        vip_group = data['vip_group'].split(',')
        vip_group_list = []
        for vip in vip_group:
            vip_port = vip.split(':')
            vip_group_list.append({
                                    "vip": vip_port[0],
                                    "port": vip_port[1]
                                })
        data['vip_group'] = vip_group_list
        for rs in data['rs']:
            rs['port'] = rs['port'].split(',')           

        #write addition into db
        handler = DB_Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstance(id, data)
        self.write(data)


#api get the real server list in the db
class LvsManagerDeployGetRsList(BaseHandler):

    def get(self):
        id = self.get_argument("id",None)
        handler = DB_Model('LvsManagerConfig')
        vipinstanceinfo = handler.getLvsManagerConfigVipInstanceInfo(id)

        if vipinstanceinfo != None:
            for i,rs in enumerate(vipinstanceinfo['rs']):
                rs['i'] = i
                rs['port'] = ','.join(rs['port'])
            self.write(json.dumps(vipinstanceinfo['rs']))
        else:
            self.write('ok')

#api offline the vip instance
class LvsManagerDeployOffline(BaseHandler):

    def post(self):
        data = json.loads(self.request.body)
        id = data['id']
        handler = DB_Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstanceToOffline(id)
        self.write('ok')

#api online the vip instance
class LvsManagerDeployOnline(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        id = data['id']
        handler = DB_Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstanceToOnline(id)
        self.write('ok')


#api delete the vip instance
class LvsManagerDeployDel(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        id = data['id']
        handler = DB_Model('LvsManagerConfig')
        handler.DelLvsManagerConfigVipInstance(id)
        self.write('ok')

#get the config from the yaml config file
def search_cluster(id):
    config = yaml.load(open(options.config))
    cluster_list = config['cluster']
    for i in cluster_list:
        if id == i['id']:
            return i
    return None

#publish via saltstack api
class LvsManagerPublish(BaseHandler):
    @tornado.web.authenticated

    def post(self):
        time_now = time.time()
        cluster_id = self.get_argument("id", None)
        mess = self.get_argument("mess", None)
        #self.write(cluster_id + ' ' + mess)
        
        area = search_cluster(cluster_id)['area']
        admin_mail_group = search_cluster(cluster_id)['admin_mail_group']

        handler = DB_Model('LvsManagerConfig')
        vipinstancelist = handler.getLvsManagerConfigVipInstanceList(cluster_id)
        _vipinstancelist = handler.getLvsManagerConfigVipInstanceList(cluster_id)

        for i in _vipinstancelist:
            i['_id'] = str(i['_id'])

        if len(vipinstancelist) == 0:
            self.write('This ' + cluster_id + ' has no vip instance configuration in the CMDB')
        else:
            #else get the lastest publish id
            handler = DB_Model('LvsManagerPublish')
            last_rev = handler.getLvsManagerPublishLastRev(cluster_id)
            if last_rev:
                rev = last_rev['rev'] + 1
            else:
                rev = 1

            #insert the lvsmanagerpublish result to the cmdb
            lvsmanagerpublish = {
                                    "time": time_now,
                                    "message": mess,
                                    "cluster_id": cluster_id,
                                    "rev": rev,
                                    "server": _vipinstancelist,
                                    "area": area,
                                    "admin_mail_group": admin_mail_group,
                                }
            new_publish_id = handler.insertLvsManagerPublish(lvsmanagerpublish)

            #dump the publish information to YAML
            context = yaml.dump(lvsmanagerpublish)

            #jinja render to create keepalived config
            keepalived_config = self.template('keepalived.tpl', vip_instance_list = vipinstancelist, cluster_id=cluster_id)            
            publishdir = options.publishdir
            keepalived_config_file = os.path.join(publishdir,new_publish_id)

            #create the config file
            f = codecs.open(keepalived_config_file, 'w+', 'utf-8')
            f.write(keepalived_config)
            f.close()
            
            #transfer the configuration to the minion
            #Get the minion
            config = yaml.load(open(options.config))
            tgt = search_cluster(cluster_id)['agent']
            source_file = keepalived_config_file
            dst_file = '/etc/keepalived/keepalived.conf'

            #transfer
            runsalt = saltstackwork()
            result = runsalt.run_publish_keepalived(tgt, source_file, dst_file)

            #dump the publish information and transfer to the minion
            info_source_file = 'info.yaml'
            info_dst_file = '/etc/keepalived/info.yaml'
            result2 = runsalt.run_cp_file(tgt, info_source_file, info_dst_file, context)
            ret_html = ''
            ret_result = True
            for lb in tgt:
                if result.has_key(lb) and result2.has_key(lb):
                    ret_html += '%s ok\n' %(lb)
                else:
                    ret_html += '%s failed\n' %(lb)
                    ret_result = False

            handler.updateLvsManagerPublishResult(new_publish_id, ret_result)
            print result
            print result2
            self.write(ret_html)
            #print ret_html

#keepalived reload handler
class LvsManagerKeepalivedReload(BaseHandler):
    @tornado.web.authenticated
    
    def get(self):

        cluster_id = self.get_argument('id', None)
        cluster = search_cluster(cluster_id)
        cluster['lb'] = []
        
        lb_list = []
        for lb in cluster['agent']:
            if search_agent(lb) != None:
                lb_list.append({
                                'id': search_agent(lb)['id'],
                                'ipadd': search_agent(lb)['ipadd'],
                                'port': search_agent(lb)['port'],
                                })
        cluster['lb'] = lb_list
                

        self.render2('lvsmanager_keepalived_reload.html', cluster = cluster) 



















####saltstackwork
class saltstackwork():
	
	def __init__(self):
		import salt.client
		self.local = salt.client.LocalClient()

	def run_publish_keepalived(self,tgt,source_file,dst_file):
		func = 'cp.recv'
		f = open(source_file,'r')
		file_data = f.read()
		f.close()
		_fn = {source_file:file_data}
		result = self.local.cmd(tgt,func,[_fn,dst_file],expr_form='list',timeout=10)
		return result

	def run_cp_file(self,tgt,source_file,dst_file,context):
		func = 'cp.recv'
		_fn = {source_file:context}
		result = self.local.cmd(tgt,func,[_fn,dst_file],expr_form='list',timeout=10)
		return result

	def run_cmd(self,tgt,cmd):
		_cmd = [cmd]
		result = self.local.cmd(tgt,'cmd.run',_cmd,expr_form='list',timeout=10)
		result_list = []
		for i in tgt:
			if result.has_key(i):
				result_list.append({"id":i,"ret":result[i],"result":True})
			else:
				result_list.append({"id":i,"result":False})
		
		return result_list





