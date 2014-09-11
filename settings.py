#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

import os
from weibosecret import user, password, blacklist

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


ENV = os.environ.get('ENV', 'DEV')
if ENV == '':
    ENV = 'DEV'

envs = {
    'DEV': {
        'USERNAME': user,
        'PASSWORD': password,
        'USERS': blacklist,
        'IMAGE_PATH': './img',
        'TIMEOUT': 60,
        'DBNAME': 'weibolog',
    },
    'PRODUCTION': {
        'USERNAME': user,
        'PASSWORD': password,
        'USERS': [
            '',
        ],
        'IMAGE_PATH': './img',
        'TIMEOUT': 60,
        'DBNAME': 'weibolog',
    },
    'TEST': {
        'USERNAME': user,
        'PASSWORD': password,
        'USERS': [
            '1839754451',
        ],
        'IMAGE_PATH': './',
        'TIMEOUT': 60,
        'DBNAME': 'weibolog',
    },
}

for key, value in envs.get(ENV, envs['DEV']).iteritems():
    globals()[key] = value
