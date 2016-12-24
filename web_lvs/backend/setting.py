#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

from tornado.options import define, options

define("mongodb", default="localhost", help="mongodb host")
define("mongodb_port", default=27017, help="mongodb port")
define("db", default="LvsMonitor", help="default Lvs Monitor Db Name")
