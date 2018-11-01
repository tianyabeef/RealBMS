CREATE TABLE auth_user
(
    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    password varchar(128) NOT NULL,
    last_login datetime,
    is_superuser bool NOT NULL,
    username varchar(150) NOT NULL,
    first_name varchar(30) NOT NULL,
    email varchar(254) NOT NULL,
    is_staff bool NOT NULL,
    is_active bool NOT NULL,
    date_joined datetime NOT NULL,
    last_name varchar(150) NOT NULL
);
CREATE UNIQUE INDEX sqlite_autoindex_auth_user_1 ON auth_user (username);
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$tZcYGMuNpaEq$+Vj3z/VzCU9g6dFbG0kWlgLshW/bR6HhsjXgmn5UiBE=', '2018-11-01 02:32:24.585308', 1, 'admin', '', '410378266@qq.com', 1, 1, '2018-10-26 01:35:43.681970', '');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$jWvCkI5fC2Wz$QVgsVX/aE3W/+07cNfat/aac0+KfT35qheHOMbqd1+k=', '2018-11-01 02:32:49.408728', 0, 'marr', '荣荣', '', 1, 1, '2016-12-26 09:25:00', '马');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$l5JCytweMnnC$JcMtmUSIOGUbQap7LvWX+H4RklifKchrinfkiZQBjI4=', '2018-10-30 10:37:12.951439', 0, 'zhoub', '斌', '', 1, 1, '2016-12-26 09:25:00', '周');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$w2N1NbmqJvGn$Xzd+fMjh2zLtYpMP46IbLxP0ZK4jqFEo5WRVTVvuU64=', '2018-10-30 02:08:07.680349', 0, 'caoz', '展', '', 1, 1, '2016-12-30 03:01:00', '曹');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$XWftwTWp1VYu$AfdCWrX8Ah8n+XHpoA5CLI8bBag7KoycyIjzJJA0h4Y=', '2018-09-12 01:56:45.882752', 0, 'fengyp', '玉萍', '', 1, 1, '2017-01-06 03:45:00', '冯');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$RVgbk1aHYP1c$p46rXDx0kjeFPNDzDJ5hyvilPDjmgMIok8STeKZ7gwE=', '2017-11-22 02:43:36.570411', 0, 'hongbz', '宝珍', '', 1, 1, '2017-01-09 07:16:00', '洪');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$6KMaII4lINIV$jZuWLjOB7jjgPhMXRFBDe9hqzFStAfQqMhMbp0U932o=', '2018-07-03 01:56:23.442335', 0, 'wangjm', '景梅', '', 1, 1, '2017-02-08 08:51:00', '王');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$4KiRwyqf9g2V$E1a+rrKoCgt6UOqkiGxCQegwA0Z2RYIuG2eAmtZ8ero=', '2018-06-30 10:14:48.057264', 0, 'zhanfx', '飞祥', '', 1, 1, '2017-02-09 06:55:00', '战');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$XfKrJCnvIgMj$WY68NRB+3AEOsj5F0n0ROlVYlwnXOMAg7ME9bIreWK4=', '2017-05-08 06:08:34.470569', 0, 'zhaojq', '建青', '', 1, 1, '2017-02-10 08:53:00', '赵');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$ACUbknFdcFQi$ZVF1EGAH3c4EbPtu3OGVZlDhSRFdP/RnJkqXtQjfdKg=', '2017-04-25 03:14:42.947939', 0, 'lixd', '晓东', '', 1, 1, '2017-02-10 08:53:00', '李');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$30000$zdANxCreyMKV$MZBC7JFfHzqRjlqKn7QsMdKusi6h32lYk/IDpmGKsNI=', '2018-09-21 02:47:31.148344', 0, 'liuq1', '强', '', 1, 1, '2017-02-10 08:54:00', '刘');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$acfbrHs3cPHY$HkRcptV55e5aPbXKf+GsmcPO0GUcx0XIRoEWhXMwyAQ=', null, 0, '1@qq.com', '', '1@qq.com', 1, 1, '2018-10-29 02:13:17.709285', '');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$FyI6PVANwLpW$yTtzTAs2uRqZZK6ZSHoNbRrHpfg5VBuPFHiZWfqXWCg=', null, 0, '4103782669@qq.com', '', '4103782669@qq.com', 1, 1, '2018-10-29 05:26:35.861661', '');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$uXkOuk88AWxw$UkYjh80PABB4E7ILywHJw9AEXIZJl6XPSfBKTxIV0kM=', '2018-10-30 02:01:52.484889', 0, '黄云', '云', '', 1, 1, '2018-10-30 01:31:00', '黄');
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) VALUES ('pbkdf2_sha256$120000$Wmhz5aImycMo$l7BkkJI/GWzojoqkw7HHxM7w93tHYUrf9FVENIY/+R0=', '2018-10-30 10:38:14.765975', 0, 'example@qq.com', '', 'example@qq.com', 1, 1, '2018-10-30 01:34:10.279817', '');