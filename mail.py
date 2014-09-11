#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

import poplib
import imaplib
import email
import os
import time

def parse_header(msg):
    subject = msg.get('subject')
    h = email.Header.Header(subject)
    subject = email.Header.decode_header(h)
    subject = unicode(subject[0][0], subject[0][1])
    name, from_email = email.utils.parseaddr( msg.get('from') )
    name, to_email = email.utils.parseaddr( msg.get('to') )
    name, cc = email.utils.parseaddr( msg.get_all('cc') )
    print subject, from_email, to_email, cc

def parse_body(msg):
    # 循环信件中的每一个mime的数据块
    for part in msg.walk():
        # 判断是否是multipart，是的话，里面的数据是一个message 列表
        if not part.is_multipart():
            charset = part.get_charset()
            print 'charset: ', charset
            contenttype = part.get_content_type()
            print 'content-type', contenttype

            name = part.get_param('name') # 如果是附件，得到附件文件名
            if name:
                # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                h = email.Header.Header(name)
                dh = email.Header.decode_header(h)
                attach_name, _ = dh[0]
                # 解码出附件数据，存储到文件
                data = part.get_payload(decode=True)
                try:
                    fd = open(os.path.basename(fname), 'wb')
                except:
                    # 附件名有非法字符，换一个
                    fd = open(str(time.time()), 'wb')
                fd.write(data)
                fd.close()
            else:
                # 不是附件，是文本内容.解码出文本内容，直接输出.
                print part.get_payload(decode=True)
        else:
            print [part.is_multipart()]
        print '+'*80


def get_email(host, username, password, port=993):
    try:
        serv = imaplib.IMAP4_SSL(host, port)
    except Exception as e:
        print e
        serv = imaplib.IMAP4(host, port)
    serv.login(username, password)
    serv.select()
    typ, data = serv.search(None, '(FROM "miraclecome@gmail.com")')

    count = 1
    pcount = 1
    for num in data[0].split()[:-1]:
        typ, data = serv.fetch(num, '(RFC822)')
        text = data[0][1]
        message = email.message_from_string(text)
        parse_header(message)
        parse_body(message)
        pcount += 1
        if pcount > count:
            break

    serv.close()
    serv.logout()


def get_popemail(host, username, password):
    """
    # 从服务器获取邮件列表:
    messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
    # Concat message pieces:
    messages = ["\n".join(mssg[1]) for mssg in messages]
    """
    pop_conn = poplib.POP3_SSL(host)
    pop_conn.user(username)
    pop_conn.pass_(password)
    number_of_email, bytes_of_email = pop_conn.stat()

    ok, mail, byte = pop_conn.retr(number_of_email)
    msg = email.message_from_string('\n'.join(mail))
    parse_header(msg)
    parse_body(msg)

    pop_conn.quit()


if __name__ == '__main__':
    host = 'pop.qq.com'
    username = '12@qq.com'
    password = 'password'
    get_popemail(host, username, password)
