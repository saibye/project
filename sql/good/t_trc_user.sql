
drop table if exists t_trc_user;

create table t_trc_user
(
   user_id              char(20) not null,
   user_name            varchar(32),
   user_mail            varchar(64),
   enable               char(1),
   inst_date            date,
   inst_time            time,
   primary key (user_id)
);

create index IDX_T_TRC_USER_1 on t_trc_user
(
   user_id
);

