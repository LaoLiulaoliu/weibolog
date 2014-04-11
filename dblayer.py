#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from pgutils import DBUtils
from settings import DBNAME

class DBLayer(object):

    def __init__(self):
        self.db = DBUtils(DBNAME)

    def upd_user(self, uid, name, description, weibo_num, follow, fans, page_num):
        """
        If user not in db, insert user info.
        If user in db, update what changes.
        """
        result = self.db.execute("select uid, name, description, weibo_num, follow, fans, page_num from person where uid=%s;",
                (uid,),
                result=True)

        if not result.results:
            self.db.execute("insert into person (uid, name, description, weibo_num, follow, fans, page_num) \
                    values (%s,%s,%s,%s,%s,%s,%s)",
                    (uid, name, description, weibo_num, follow, fans, page_num))
            return

        name = name.encode('utf-8')
        description = description.encode('utf-8')
        result = dict( zip(result.columns, result.results[0]) )
        update = "update person set "
        begin_length = len(update)
        update += "name='"+name+"'," if name != result['name'] else ""
        update += "description='"+description+"'," if description != result['description'] else ""
        update += "weibo_num="+str(weibo_num)+"," if weibo_num != result['weibo_num'] else ""
        update += "follow="+str(follow)+"," if follow != result['follow'] else ""
        update += "fans="+str(fans)+"," if fans != result['fans'] else ""
        update += "page_num="+str(page_num)+"," if page_num != result['page_num'] else ""
        if begin_length != len(update):
            update = update[:-1] + " where uid='" + uid + "';"
            self.db.execute(update)

    def upd_weibo(self, wbid, uid, content, pubtime, device, pictures, attitude_num, attitudes, comment_num, repost_num, forward=None, uid_=None):
        """
        If weibo not in db, insert weibo.
        If weibo in db, only update the fields that can be changed.
        """
        result = self.db.execute("select wbid, uid, content, forward, uid_, pubtime, device,\
            pictures, attitude_num, attitudes, comment_num, repost_num from weibo where wbid=%s;",
            (wbid,),
            result=True)
        if not result.results:
            self.db.execute("insert into weibo (wbid, uid, content, forward, uid_, pubtime,\
                device, pictures, attitude_num, attitudes, comment_num, repost_num) values \
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (wbid, uid, content, forward, uid_, pubtime, device, pictures,
                attitude_num, attitudes, comment_num, repost_num))
            return
        result = dict( zip(result.columns, result.results[0]) )
        update = "update weibo set "
        begin_length = len(update)
        if attitude_num > result['attitude_num']:
            update += "attitude_num="+str(attitude_num)+","
            update += "attitudes=%s,"

        update += "comment_num="+str(comment_num)+"," if comment_num != result['comment_num'] else ""
        update += "repost_num="+str(repost_num)+"," if repost_num != result['repost_num'] else ""
        if begin_length != len(update):
            update = update[:-1] + " where wbid='" + wbid + "';"
            self.db.execute(update, (attitudes, ))

    def upd_comment(self, commentid, wbid, name, uid_, reply, reply_time):
        """
        If comment not in db, insert the comment.
        If comment in db, not touch it.
        If comment delete from weibo, not touch it in our db.
        """
        result = self.db.execute("select commentid, wbid, name, uid_, reply, reply_time \
                from comment where commentid=%s;",
                (commentid,),
                result=True)
        if not result.results:
            self.db.execute("insert into comment (commentid, wbid, name, uid_, reply,\
                reply_time) values (%s,%s,%s,%s,%s,%s)",
                    (commentid, wbid, name, uid_, reply, reply_time))
            return

