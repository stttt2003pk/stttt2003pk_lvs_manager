#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

from tornado.options import define, options

define("mongodb", default="localhost", help="mongodb host")
define("mongodb_port", default=27017, help="mongodb port")
define("db", default="LvsMonitor", help="default Lvs Monitor Db Name")

define("https_url", default="https://sso.stttt2003pk.com/", help="https url")
define("lvs_url", default="http://lvs.stttt2003pk.com/", help="lvs_url")
