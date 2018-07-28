
drop table if exists tbl_day_sina;

/*==============================================================*/
/* Table: tbl_day_sina                                               */
/*==============================================================*/
create table tbl_day_sina
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   deal_total_count     float,
   deal_total_amount    float,
   inst_date            date,
   inst_time            time,
   up_date              date,
   primary key (pub_date, stock_id, stock_loc)
);

/*==============================================================*/
/* Index: IDX_TBL_DAY_SINA_1                                         */
/*==============================================================*/
create index IDX_TBL_DAY_SINA_1 on tbl_day_sina
(
   stock_id
);

create index IDX_TBL_DAY_SINA_2 on tbl_day_sina
(
   pub_date
);

