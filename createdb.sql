create database weibolog;
\c weibolog
create table person (
  id serial primary key,
  uid varchar(12) unique,
  urlmark varchar(64),
  name varchar(32),
  old_name varchar(32),
  description varchar(256),
  weibo_num integer,
  follow integer,
  fans integer,
  page_num integer
);
create index person_urlmark on person (urlmark);
create index person_name on person (name);

create table weibo (
  wbid varchar(10) primary key,
  uid varchar(12) references person (uid) on delete restrict not null,
  content varchar(280),
  forward varchar(280),
  uid_ varchar(64),
  pubtime timestamp,
  device varchar(32),
  pictures varchar(256)[],
  attitude_num integer,
  attitudes varchar(64)[],
  comment_num integer,
  repost_num integer
);
create index weibo_uid on weibo (uid);

create table comment (
  commentid bigint primary key,
  wbid varchar(10) references weibo (wbid) on delete cascade not null,
  name varchar(32),
  uid_ varchar(64),
  reply varchar(300),
  reply_time timestamp
);
create index comment_wbid on comment (wbid);
