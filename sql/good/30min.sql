drop table if exists tbl_30min;

/*==============================================================*/
/* Table: tbl_30min                                             */
/*==============================================================*/
create table tbl_30min
(
   pub_date_time        datetime,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   deal_total_count     float,
   deal_total_amount    float,
   pub_date             date,
   pub_time             time,
   inst_date            date,
   inst_time            time,
   up_date              date,
   primary key (pub_date_time, stock_id, stock_loc)
);

/*==============================================================*/
/* Index: IDX_TBL_30MIN_1                                       */
/*==============================================================*/
create index IDX_TBL_30MIN_1 on tbl_30min
(
   stock_id
);

create index IDX_TBL_30MIN_2 on tbl_30min
(
   pub_date_time
);

