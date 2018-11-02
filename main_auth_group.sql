CREATE TABLE auth_group
(
    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    name varchar(80) NOT NULL
);
CREATE UNIQUE INDEX sqlite_autoindex_auth_group_1 ON auth_group (name);
INSERT INTO auth_group (name) VALUES ('实验部');
INSERT INTO auth_group (name) VALUES ('项目管理');
INSERT INTO auth_group (name) VALUES ('业务员（销售）');
INSERT INTO auth_group (name) VALUES ('市场部');
INSERT INTO auth_group (name) VALUES ('财务部');
INSERT INTO auth_group (name) VALUES ('业务员（公司）');
INSERT INTO auth_group (name) VALUES ('销售总监');
INSERT INTO auth_group (name) VALUES ('合作伙伴');
INSERT INTO auth_group (name) VALUES ('生物信息部');
INSERT INTO auth_group (name) VALUES ('生物信息总监');
INSERT INTO auth_group (name) VALUES ('实验总监');
INSERT INTO auth_group (name) VALUES ('市场总监');