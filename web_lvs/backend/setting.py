#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

from tornado.options import define, options

#define domain port 
domain_name = 'lvs.stttt2003pk.com'
port = int(8888)
#lvs_url = 'http://lvs.stttt2003pk.com/'

define("debug",default=True,help="Debug Mode",type=bool)

define("port", default=port, help="the servers run the default port", type=int)
define("mongodb", default="127.0.0.1", help="mongodb host")
define("mongodb_port", default=27017, help="mongodb port")
define("db", default="Lvs_stttt2003pk_manager", help="default lvs Db Name")

#cookie
define("cookies_expires", default=1,help="cookies_expires_days")

#url+port
lvs_url_port = 'http://' + domain_name + ':' + str(port) + '/'
define("lvs_url", default=lvs_url_port, help="lvs_url_port")

