
mysql -hsai-mysql -u root -p

create database tu default character set utf8;
create user tudev identified by '123456';

grant select,insert,update,delete,create,drop  on tu.* to tudev;
grant all privileges on tu.* to tudev@"%";
FLUSH   PRIVILEGES;

------------------------------------------------------------------------

export LANG=zh_CN.utf8

alias my='mysql -hsai-mysql -u tudev -Dtu -p123456'

------------------------------------------------------------------------
use tu
create table tbl_test
(
   INST_DATE            date not null,
   INST_TIME            time not null,
   HQ_ID                char(8) not null,
   HQ_NAME              varchar(20),
   CURR_POINT           float,
   DEAL_AMOUNT          int,
   primary key (INST_DATE, HQ_ID)
);


insert into tbl_test values ('1977-07-07', '21:31:00', '000811', 'XX', 4199, 200);
insert into tbl_test values ('2015-06-28', '21:31:00', '000811', '烟台冰轮', 4199, 200);

------------------------------------------------------------------------
