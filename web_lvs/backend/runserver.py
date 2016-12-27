import os
import tornado.web
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options

from tornado.options import define, options
from setting import *

import control

cur_dir = os.path.dirname(os.path.abspath(__file__))

class Application(tornado.web.Application):
	def __init__(self):
		web_path = [
			(r"/", control.HomeHandler),	
			(r"/login", control.Login),
			(r"/login_auth", control.LoginAuth),
		]

		handlers = web_path

		settings = dict(
			template_path=os.path.join(cur_dir,'templates/'),
			static_path=os.path.join(cur_dir,'lib/'),
			cookie_secret="SunRunVas38288446TestStttt2003pk",
			login_url="/",
		)
		tornado.web.Application.__init__(self, handlers,**settings)

def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
