#!/usr/bin/env python
# -*- coding: utf8 -*-

from control import *

template_test = TemplateRendering()
template_test.render_template('login.html', STATIC_URL='/static/')
