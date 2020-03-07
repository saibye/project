
drop table if exists t_trc_reg;

create table t_trc_reg
(
   user_id              char(20) not null,
   stock_id             char(8) not null,
   inst_date            date,
   inst_time            time,
   primary key (user_id, stock_id)
);

create index IDX_T_TRC_REG_1 on t_trc_reg
(
   user_id,
   stock_id
);

