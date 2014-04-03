#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from datetime import datetime, timedelta
import os
import re
import time
import glob
import lxml.html

from settings import USERS, IMAGE_PATH, TIMEOUT
from login import Login
from dblayer import DBLayer

def time_convert(time_str):
    """
    text_content() type is <type 'lxml.etree._ElementUnicodeResult'>, we need encode
    '03月16日 23:54'
    '今天 21:07'
    '3分钟前'
    '2013-10-31 16:46:52'
    ?? '2013-10-18 00:06'
    """
    now = datetime.now().replace(microsecond=0, second=0)
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    date = year + '-' + month + '-' + day

    time_str = time_str.encode('utf-8')
    if '今天' in time_str:
        time_str = time_str.replace('今天', date)
        result = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    elif '分钟前' in time_str:
        n_min = int( time_str[:time_str.find('分钟前')] )
        result = now - timedelta(minutes=n_min)
    elif '月' in time_str and '日' in time_str:
        n_month, rest = time_str.split('月')
        n_day, rest = rest.split('日')
        n_hour, n_min = rest.split(':')
        result = now.replace(month=int(n_month),
                    day=int(n_day),
                    hour=int(n_hour),
                    minute=int(n_min))
    else:
        result = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return result


class Crawler(object):

    def __init__(self):
        self.url = 'http://weibo.cn/u/'
        self.siteurl = 'http://weibo.cn'
        self.db = DBLayer()
        self.session = Login().get_login_session()

    def get_html(self, url):
        """
        "<html><body>\nThe server didn't respond in time.<br>\nplease try again later<br>\n</body></html>"
        "After about 3 times trying, this weibo accout always redirect to http://weibo.cn/pub"
        """
        for i in range(3):
            try:
                ret = self.session.get(url, timeout=TIMEOUT)
            except:
                continue
            if "The server didn't respond in time.<br>\nplease try again later<br>" in ret.content:
                print "Stop Your Crawling!"
                time.sleep(TIMEOUT)
            else: break
        else:
            return
        time.sleep(5)
        html = lxml.html.fromstring(ret.content)
        return html

    def run(self):
        """
            crawl user one by one
        """
        for user in USERS:
            self.get_userpage(user)

    def get_userpage(self, userid):
        """
            update user info
            get every weibo of user
        """
        html = self.get_html(self.url + userid)

        name, description, weibo_num, follow, fans, page_num = self.get_person_info(html)
        self.db.upd_user(userid, name, description, weibo_num, follow, fans, page_num)

        for weibo in html.cssselect('div.c'):
            self.get_weibo_item( weibo, userid )

        for page in range(2, page_num+1):
            link = self.url + userid + '?page=' + str(page)
            print userid, page
            html = self.get_html(link)
            for weibo in html.cssselect('div.c'):
                self.get_weibo_item( weibo, userid )

    def get_person_info(self, html):
        name = html.cssselect('div.u table div.ut .ctt')[0].text
        if name.find('[') != -1: # [在线]
            name = name[:name.find('[')]

        desc = html.cssselect('div.u table div.ut .ctt')
        desc.pop(0)
        description = ''
        for i in desc:
            description += '; ' + i.text_content()
        if description.startswith('; '):
            description = description[2:]

        page_num = html.cssselect('#pagelist form div input[name=mp]')[0].get('value')
        statistics = html.cssselect('div.u .tip2')[0]
        weibo_num = statistics.cssselect('.tc')[0].text_content()
        weibo_num = weibo_num[weibo_num.find('[')+1:weibo_num.find(']')]
        for ia in statistics.cssselect('a'):
            link = ia.get('href')
            if 'follow?' in link:
                follow = ia.text_content()
                follow = follow[follow.find('[')+1:follow.find(']')]
            elif 'fans?' in link:
                fans = ia.text_content()
                fans = fans[fans.find('[')+1:fans.find(']')]
        return name, description, int(weibo_num), int(follow), int(fans), int(page_num)

    def get_weibo_item(self, weibo, userid):
        weiboid = weibo.get('id')
        if weiboid is None: # other 'div.c' element
            return
        weiboid = weiboid.split('_')[-1] # M_ADpwMx9JE
        div_xpath = weibo.xpath('./div')
        span = div_xpath[0].cssselect('span:first-of-type')[0].get('class')
        if span == 'cmt':
            is_forward = True
        elif span == 'ctt':
            is_forward = False
        else:
             raise Exception("Exception of weibo element div: {}, {}".format(userid, weiboid))

        attitude_num, repost_num, comment_num = self.get_interact_num(div_xpath[-1], delete=True)
        public_info = div_xpath[-1].cssselect('span.ct')[0]
        pubtime, device = public_info.text_content().split(u'来自')
        pubtime, device = pubtime.strip(), device.strip()
        pubtime = time_convert(pubtime)
        public_info.drop_tree()

        if is_forward:
            forward = div_xpath[0].xpath('./span[@class="ctt"]')[0].text_content()
            originaler = div_xpath[0].xpath('./span[@class="cmt"]/a[@href]') # {uid: name}
            if not originaler: # <span class="cmt">转发了微博：</span> 微博被删除连作者都看不到了
                uid_ = None
            else:
                name = originaler[0].text_content()
                href = originaler[0].get('href')
                uid_ = self.from_link_to_uid_(href) + '_' + name

            div_xpath[-1].xpath('./span[@class="cmt"]')[0].drop_tree() # 转发理由:
            content = div_xpath[-1].text_content().strip()
        else:
            forward, uid_ = None, None
            content = div_xpath[0].cssselect('span.ctt')[0].text_content()

        attitudes = self.get_attitude(weiboid) if attitude_num != 0 else []
        pictures = self.get_pic(weiboid)
        self.db.upd_weibo(weiboid, userid, content, pubtime, device, pictures, attitude_num, attitudes, comment_num, repost_num, forward, uid_)

        if comment_num != 0:
            self.get_comment(weiboid)


    def get_interact_num(self, node, delete=False):
        attitude_num, repost_num, comment_num = None, 0, 0
        for ia in node.xpath('./a[@href]'):
            link = ia.get('href')
            if 'http://weibo.cn/attitude/' in link:
                attitude = ia.text_content()
                attitude_num = int( attitude[attitude.find('[')+1:attitude.find(']')] )
                if delete: ia.drop_tree()
            elif 'http://weibo.cn/repost/' in link:
                repost = ia.text_content()
                repost_num = int( repost[repost.find('[')+1:repost.find(']')] )
                if delete: ia.drop_tree()
            elif 'http://weibo.cn/comment/' in link:
                comment = ia.text_content()
                comment_num = int( comment[comment.find('[')+1:comment.find(']')] )
                if delete: ia.drop_tree()
            elif 'http://weibo.cn/fav/addFav/' in link:
                if delete: ia.drop_tree()

        if attitude_num == None: # <span class="cmt">已赞[2]</span>
            ia = node.cssselect('span.cmt')[0]
            attitude = ia.text_content()
            attitude_num = int( attitude[attitude.find('[')+1:attitude.find(']')] )
            if delete: ia.drop_tree()
        return attitude_num, repost_num, comment_num


    def get_attitude(self, weiboid):
        attitudes = []
        attitude_link = 'http://weibo.cn/attitude/' + weiboid
        attitude = self.get_html(attitude_link)
        for laud in attitude.cssselect('div.c'):
            laud_time = laud.xpath('./span[@class="ct"]')
            if laud_time == []:
                continue
            laud_time = time_convert( laud_time[0].text_content() )
            laud = laud.cssselect('a:first-of-type')[0]
            name = laud.text_content()
            href = laud.get('href')
            uid = self.from_link_to_uid_(href)
            attitudes.append( '_'.join( [uid, name, str(laud_time)] ) )
        return attitudes

    def get_comment(self, weiboid):
        comment_link = 'http://weibo.cn/comment/' + weiboid
        comment = self.get_html(comment_link)
        for reply in comment.cssselect('div.c[id^=C_]'):
            commentid = reply.get('id').split('_')[-1]
            reply_time = reply.find_class('ct')[0].text_content().split()
            reply_time = time_convert(reply_time[0] + ' ' + reply_time[1])

            replyer = reply.cssselect('a:first-of-type')[0]
            name = replyer.text_content()
            href = replyer.get('href')
            uid = self.from_link_to_uid_(href)

            content = reply.find_class('ctt')[0].text_content()
            reply = name + ': ' + content
        
            self.db.upd_comment(commentid, weiboid, name, uid, reply, reply_time)


    def get_pic(self, weiboid):
        """
            must use login session
            http://weibo.cn/mblog/picAll/weiboid
        """
        paths = []
        try:
            ret = self.session.get('http://weibo.cn/mblog/picAll/' + weiboid, timeout=TIMEOUT)
        except:
            ret = self.session.get('http://weibo.cn/mblog/picAll/' + weiboid, timeout=TIMEOUT)
        picurls = re.findall('<a href="([0-9a-zA-Z/?=&]+?)">原图</a>', ret.content)
        path_prefix = os.path.join(IMAGE_PATH, weiboid + '_')
        saved_imgs = glob.glob(path_prefix + '*')
        if len(saved_imgs) >= len(picurls):
            return saved_imgs

        count = 0
        for picurl in picurls:
            count += 1
            try:
                cont = self.session.get(self.siteurl + picurl).content
            except:
                cont = self.session.get(self.siteurl + picurl).content
            path = path_prefix + str(count) + '.jpg'
            with open(path, 'wb') as fd:
                fd.write(cont)
            paths.append(path)
        return paths

    def from_link_to_uid_(self, href):
        """
        http://weibo.cn/watermark? # `urlmark`
        http://weibo.cn/u/234545? # `uid`
        """
        if '/u/' in href:
            uid = href[:href.find('?')].split('/')[-1]
            user_id = 'i_' + uid
        else:
            urlmark = href[:href.find('?')].split('/')[-1]
            user_id = 'm_' + urlmark
        return user_id


    def unit_test(self):
        print self.get_pic('AgzIG6CHo') # 0 pic

#        ret = self.session.get('http://weibo.cn/u/1839754451')
#        open('login.html', 'w').write(ret.content)
#        print self.session.headers

#        print self.get_pic('ADpwMx9JE') # 1 pic
#        print self.get_pic('AeuC772bW') # 4 pic
#        self.get_attitude('AgzIG6CHo') # 0 attitude
#        self.get_comment('AgzIG6CHo') # 0 comment
#        self.get_attitude('ADpwMx9JE') # 2 attitude
#        self.get_comment('AAsUnzdZl') # 8 comment



if __name__ == '__main__':
    Crawler().unit_test()
