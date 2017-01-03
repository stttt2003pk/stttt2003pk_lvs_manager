#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options
import tornado.web
from tornado.escape import json_decode

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

####real server alived html
def rs_is_lived(weight):
	if int(weight) == 0:
		return False
	else:
		return True

####manager admin acount
def user_is_manager(user):
	handler = Model('LvsAccount')
	user_info = handler.getAccountOne(user)
	if user_info['is_manager'] or user_info['is_super_manager']:
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

####















####saltstackwork
class saltstackwork():
	
	def __init__(self):
		import salt
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





