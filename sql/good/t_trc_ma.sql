
drop table if exists t_trc_ma;

create table t_trc_ma
(
   user_id              char(20) not null,
   ma                   int not null,
   inst_date            date,
   inst_time            time,
   primary key (user_id, ma)
);

create index IDX_T_TRC_MA_1 on t_trc_ma
(
   user_id,
   ma
);

