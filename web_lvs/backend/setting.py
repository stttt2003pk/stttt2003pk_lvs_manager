#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

from tornado.options import define, options

define("port", default=8888, help="the servers run the default port", type=int)

define("mongodb", default="localhost", help="mongodb host")
define("mongodb_port", default=27017, help="mongodb port")
define("db", default="LvsMonitor", help="default Lvs Monitor Db Name")

define("lvs_url", default="http://lvs.stttt2003pk.com/", help="lvs_url")
