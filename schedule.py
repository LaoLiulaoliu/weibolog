#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from crawler import Crawler

class Schedule(object):
    def __init__(self):
        self.crawler = Crawler()

    def run(self):
        self.crawler.run()

if __name__ == '__main__':
    Schedule().run()
