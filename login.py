#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from settings import USERNAME, PASSWORD
import requests
import lxml.html
requests.adapters.DEFAULT_RETRIES = 3

def get_session():
    """.. :py:method::
    """
    if not hasattr(get_session, 'session'):
        session = requests.Session()
        session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
        get_session.session = session
    return get_session.session


class Login(object):

    uselsess_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Host': 'login.weibo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36',
    }

    data = {
        'mobile': USERNAME,
        'remember': 'on',
        'submit': '登录',
#        'password_8202': PASSWORD,
#        'backURL': 'http%3A%2F%2Fweibo.cn%2Flogin',
#        'backTitle': '新浪微博',
#        'tryCount': '',
#        'vk': '8202_653a_2216381998',
#        'code': 'kwlj',
#        'capId': '2_ccbdc8398cb418de',
    }

#    posturl = 'http://login.weibo.cn/login/?rand=1759580283&backURL=http%3A%2F%2Fweibo.cn&backTitle=%E6%89%8B%E6%9C%BA%E6%96%B0%E6%B5%AA%E7%BD%91&vt=4'

    def __init__(self):
        self._login = None
        self.loginurl = 'http://login.weibo.cn/login/'
        self.session = get_session()

    def login(self):
        """
        data `password_??` and `vk??` need update as time goes by.
        So, we get them in login page and post them all.
        `rand` in `posturl` also in login page's `form action`, but it is not important.
        """
        back = self.session.get(self.loginurl)

        html = lxml.html.fromstring(back.content)
        password = html.cssselect('.c form input[type=password]')[0].get('name')
        for i in html.cssselect('.c form input[type=hidden]'):
            self.data[i.get('name')] = i.get('value')
        self.data[password] = PASSWORD

        posturl = self.loginurl + html.cssselect('.c form[method=post]')[0].get('action')

        print('http://weibo.cn/interface/f/ttt/captcha/show.php?cpt={}'.format(self.data['capId']))
        self.data['code'] = raw_input('input captcha code: ')

        self.session.post(posturl, data=self.data)
        self._login = True

    def get_login_session(self):
        if self._login != True:
            self.login()
        return self.session

