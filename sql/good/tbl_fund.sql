
drop table if exists tbl_fund;

/*==============================================================*/
/* Table: tbl_fund                                               */
/*==============================================================*/
create table tbl_fund
(
   stock_id             char(8)  not null,
   stock_name           char(20),
   report_date          date not null,
   inst_num             int,
   inst_changed         int,
   hold_volume          float,
   volume_changed       float,
   hold_amount          float,
   hold_ratio           float,
   inst_date            date,
   inst_time            time,
   primary key (stock_id, report_date)
);

/*==============================================================*/
/* Index: IDX_TBL_FUND_1                                      */
/*==============================================================*/
create index IDX_TBL_FUND_1 on tbl_fund ( stock_id);

/*==============================================================*/
/* Index: IDX_TBL_FUND_2                                      */
/*==============================================================*/
create index IDX_TBL_FUND_2 on tbl_fund ( report_date);

