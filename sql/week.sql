drop table if exists tbl_week;

/*==============================================================*/
/* Table: tbl_week                                              */
/*==============================================================*/
create table tbl_week
(
   pub_date             date,
   stock_id             char(8) not null,
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
   primary key (pub_date, stock_id)
);

/*==============================================================*/
/* Index: IDX_TBL_WEEK_1                                       */
/*==============================================================*/
create index IDX_TBL_WEEK_1 on tbl_week
(
   stock_id
);

create index IDX_TBL_WEEK_2 on tbl_week
(
   pub_date
);

