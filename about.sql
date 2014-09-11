create database person;
\c person
create table person_info (
  id bigserial primary key,
  name varchar(32),
  sex boolean,
  birth date,
  phone varchar(16)[],
  IDcard varchar(20),
  province smallint,
  city smallint,
  address varchar(128),
  email varchar(64),
  password varchar(32),

  blacklist boolean,
  description varchar(256),
  label varchar(16)[],
  relation varchar(16)[]
);
create index p_name_idx on person_info (name);
create index p_phone_idx on person_info (phone);
create index p_id_idx on person_info (IDcard);
create index p_email_idx on person_info (email);

create table black_base_site (
  id bigint primary key,
  wbuid varchar(12)[],
  baikeid integer,
  wechatid varchar(64),
  wechat_name varchar(64),
  blogurl varchar(256),
  others json
);


create database blog;
\c blog
create table sitelist (
  id bigint,
  homeurl varchar(256),
  site varchar(16),
  uid varchar(32),
  keywords varchar(32)[],
  primary key (id, homeurl)
);

create table blog_info (
  id bigint,
  uid varchar(32),
  article_id varchar(32),
  url varchar(256),
  title varchar(128),
  content text,
  primary key (id, uid, article_id)
);


create database blacklist;
\c blacklist
create table blacklist_track (
  id bigint,
  event_time timestamp,
  place varchar(32),
  people varchar(16)[],
  talk text[],
  primary key (id, event_time)
);

create table blacklist_news (
  id bigint,
  url varchar(512),
  title varchar(128),
  news_time timestamp,
  content text,
  primary key (id, url)
);





--create table user_log (
--  id bigint,
--  record_time timestamp,
--  location varchar(64),
--  content text,
--  primary key(id, record_time)
--);
--
--create table work_record (
--  id bigserial primary key,
--  event_time timestamp,
--  place varchar(32),
--  people varchar(16)[],
--  purpose varchar(256),
--  background varchar(256),
--  brief text
--);
