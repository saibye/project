
drop table if exists tbl_profit;

/*==============================================================*/
/* Table: tbl_profit                                               */
/*==============================================================*/
create table tbl_profit
(
   stock_id             char(8) not null,
   report_date          date not null,
   year                 char(4),
   divi                 float,
   shares               int,
   inst_date            date,
   inst_time            time,
   primary key (stock_id, report_date)
);

/*==============================================================*/
/* Index: IDX_TBL_PROFIT_1                                      */
/*==============================================================*/
create index IDX_TBL_PROFIT_1 on tbl_profit ( stock_id);

