#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from pgwrapper import PGWrapper
from settings import DBNAME

class DBLayer(PGWrapper):

    def __init__(self, db=DBNAME):
        super(DBLayer, self).__init__(db)

    def upd_user(self, uid, name, sex, province, description, weibo_num, follow, fans, page_num):
        """
        If user not in db, insert user info.
        If user in db, update what changes.
        """
        result = super(DBLayer, self).execute("select uid, name, sex, province, description, weibo_num, follow, fans, page_num from person where uid=%s;",
                (uid,),
                result=True)

        if not result.results:
            super(DBLayer, self).execute("insert into person (uid, name, sex, province, description, weibo_num, follow, fans, page_num) \
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (uid, name, sex, province, description, weibo_num, follow, fans, page_num))
            return

        name = name.encode('utf-8')
        description = description.encode('utf-8')
        result = dict( zip(result.columns, result.results[0]) )
        update = "update person set "
        begin_length = len(update)
        update += "name='"+name+"'," if name != result['name'] else ""
        update += "sex="+str(sex).lower()+"," if sex != result['sex'] else ""
        update += "province="+str(province)+"," if province != result['province'] else ""
        update += "description='"+description+"'," if description != result['description'] else ""
        update += "weibo_num="+str(weibo_num)+"," if weibo_num != result['weibo_num'] else ""
        update += "follow="+str(follow)+"," if follow != result['follow'] else ""
        update += "fans="+str(fans)+"," if fans != result['fans'] else ""
        update += "page_num="+str(page_num)+"," if page_num != result['page_num'] else ""
        if begin_length != len(update):
            update = update[:-1] + " where uid='" + uid + "';"
            super(DBLayer, self).execute(update)

    def upd_weibo(self, wbid, uid, content, pubtime, device, pictures, attitude_num, attitudes, comment_num, repost_num, forward=None, uid_=None):
        """
        If weibo not in db, insert weibo.
        If weibo in db, only update the fields that can be changed.
        """
        result = super(DBLayer, self).execute("select wbid, uid, content, forward, uid_, pubtime, device,\
            pictures, attitude_num, attitudes, comment_num, repost_num from weibo where wbid=%s;",
            (wbid,),
            result=True)
        if not result.results:
            super(DBLayer, self).execute("insert into weibo (wbid, uid, content, forward, uid_, pubtime,\
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
            if 'attitudes=%s' in update:
                super(DBLayer, self).execute(update, (attitudes, ))
            else:
                super(DBLayer, self).execute(update)

    def upd_comment(self, commentid, wbid, name, uid_, reply, reply_time):
        """
        If comment not in db, insert the comment.
        If comment in db, not touch it.
        If comment delete from weibo, not touch it in our db.
        """
        result = super(DBLayer, self).execute("select commentid, wbid, name, uid_, reply, reply_time \
                from comment where commentid=%s;",
                (commentid,),
                result=True)
        if not result.results:
            super(DBLayer, self).execute("insert into comment (commentid, wbid, name, uid_, reply,\
                reply_time) values (%s,%s,%s,%s,%s,%s)",
                    (commentid, wbid, name, uid_, reply, reply_time))
            return


    def latest_public_time(self, uid):
        """ select one account's latest weibo public time,
            If this user is not been crawled before, return False
        """
        ret = super(DBLayer, self).execute('select pubtime from weibo where uid=%s order by pubtime desc limit 1;',
                              (uid,),
                              result=True)
        return False if ret.results == [] else ret.results[0][0]

