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

* rewrite the jinja2 render api to deal with tornado, so every page my rend from this template function
* have configuration and user infomation handle in this lines

### Saltstack localclient api encapsulation

### Database model

### Pure-Javascript Using(it s easy)

## References

## Plan&Vision