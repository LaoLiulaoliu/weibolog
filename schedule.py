#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from crawler import Crawler

class Schedule(object):
    def __init__(self):
        self.crawler = Crawler()

    def run(self, update=None):
        self.crawler.run(update)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='run schedule')
    parser.add_argument('--upd', '-u', type=bool, default=False, help='')
    option = parser.parse_args()
    Schedule().run(option.upd)

if __name__ == '__main__':
    main()
