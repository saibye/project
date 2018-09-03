drop table if exists tbl_name;

/*==============================================================*/
/* Table: tbl_name                                          */
/*==============================================================*/
create table tbl_name
(
   stock_id             char(8) not null,
   stock_old_name       varchar(20) not null,
   stock_new_name       varchar(20) not null,
   inst_date            date not null,
   inst_time            time not null,
   primary key (stock_id, stock_old_name)
);

create index IDX_TBL_NAME_1 on tbl_name(stock_id);
create index IDX_TBL_NAME_2 on tbl_name(inst_date);

