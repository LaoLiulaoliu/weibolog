Specification
=============
You can back up your sina weibo.
**I use gevent to speed up the crawling, my account was blocked by weibo.cn**
**So I simulate human click by requests without gevent**


Software Infrastructure
=======================


Database Consider
-----------------
levedb is not suitable, user postgresql.
I do not like mongodb!


Logic
-----
+ If hava data in database, supplement the newer data.



Every weibo item have 4 kinds of div combination
------------------------------------------------
1: get Forward[0] and Content[-1]

    <div>Forward</div> class="cmt"
    <div>picture</div>
    <div>Content</div> class="ctt"

    <div>Forward</div> class="cmt"
    <div>Content</div> class="ctt"


2: get Content[0]

    <div>Content</div> class="ctt"
    <div>picture</div>

    <div>Content</div> class="ctt"

we judge the first `div` to see whether this weibo is forward

TODO
----
+ If your weibo account is important, a identifying code image appears. (not implement yet)
+ If no data in database, add latest 100 weibo in db. (not implement yet)
+ If given a time period, crawl the period time. (not implement yet)
