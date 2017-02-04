# Lvs Manager By Stttt2003pk

## Introduction

**stttt2003pk_lvs_manager** is a friendly Web UI to manage the keepalived and monitoring the lvs maching

```
It is a demo for my company development,using some tools and CMDB
I ve try to learn Javascript(jq, jq-ui, jq plugin), MongoDb.
I will share some parts of the core code(python/js/mongo_model)
```

* Using Tornado as the WebFramework
* Saltstack help us to trancsfer configuration file and the publish_information
* MongoDB as an CMDB
* Overwrite the Jinja2 methods for rendering the html
* Base ajax using to connect the front and then Backend
* Base bootstrap css

## Core Code Shared

### BaseHandler

![](https://raw.github.com/stttt2003pk/stttt2003pk_lvs_manager/master/screenshot/basehandler.png)

```
class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
	####render2 method
	def render2(self, template_name, **kwargs):

		kwargs.update({
			'settings': self.settings,
			......
            #{{ current_user }}
			'current_user':self.get_current_user(),

		})

		content = self.render_template(template_name, **kwargs)
		self.write(content)

	def template(self, template_name, **kwargs):

		kwargs.update({
			......
		})

		content = self.render_template(template_name, **kwargs)
		return content
```

* Rewrite the jinja2 render api to deal with tornado, so every page my rend from this template function
* Have configuration and user infomation handle in this lines

### Saltstack localclient api encapsulation

* From saltstatck api documentations,we can learn that using saltstack to transfer the configuration file my be the best solution cause it has a good speed up and multiprocess non-blocking transmition
* Not like somebody s system,they can control the  highstates files to help controlling multiply servers
* I using the salt.client.LocalClient api to make this module work

```
class saltstackwork():
	def __init__(self):
		import salt.client
		self.local = salt.client.LocalClient()
    ......

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
```

![](https://raw.github.com/stttt2003pk/stttt2003pk_lvs_manager/master/screenshot/saltwork.png)

* We make the operation by

```
        runsalt = saltstackwork()
            cmd_result = runsalt.run_cmd(lb_list, cmd)

```

### Database model

![](https://raw.github.com/stttt2003pk/stttt2003pk_lvs_manager/master/screenshot/database.png)

* Using version2.7 pymongo(do not use the latest version, it is very hard)
* Choose mongo,because it s very suitable for json,in Centos7,yum provides me mariadb5.5,but i do not know why it did not support json,so the MongoDB was choosen

```
class mongo_conn():
	def __init__(self):
		self.conn = Connection(options.mongodb,options.mongodb_port)
	def db(self):
		return self.conn[options.db]

####which method call which function
class DB_Model():
    def __init__(self, method):
        self.method = method
        self.mongo = mongo_conn()
        self.db = self.mongo.db()

    def getAccountOne(self,user):
        result = self.db['LvsAccount'].find_one({"user":user})
        return result

    def insertLvsManagerConfigVipInstance(self, data):
        self.db['LvsManagerConfig'].insert(data, manipulate=False)
        return True
```

### Pure-Javascript Using(it s easy)

* Base ajax communicate with the api
* Helping to make the front logic
* [configuration&edition might be the most dificult part](https://github.com/stttt2003pk/stttt2003pk_lvs_manager/blob/master/web_lvs/backend/templates/lvsmanager_deploy_edit.html)
**Status and charts,well i do not know how to build even though i had wasted a lot of time learning Echarts**

## References

[salt.client.LocalClient](https://docs.saltstack.com/en/latest/ref/clients/index.html#localclient)

[salt.modules](https://docs.saltstack.com/en/latest/ref/modules/all/salt.modules.file.html#module-salt.modules.file)

[Tornado](http://www.tornadoweb.org/en/stable/webframework.html)

[PyMongo](https://api.mongodb.com/python/2.7.2/api/index.html)

## Plan&Vision
* Should improve the monitoring(charts plugin it is hard)
* Do some monitoring in another project
* Now we can use this mode to finished lvs/f5/nginx/haproxy configuration in multiply servers