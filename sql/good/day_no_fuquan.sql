drop table if exists tbl_day_no_fuquan;

/*==============================================================*/
/* Table: tbl_day_no_fuquan                                     */
/*==============================================================*/
create table tbl_day_no_fuquan
(
   pub_date             date not null,
   stock_id             char(8) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   deal_total_count     float,
   deal_total_amount    double,
   inst_date            date not null,
   inst_time            time not null,
   primary key (pub_date, stock_id)
);


create index IDX_DAY_NO_FUQUAN_1 on tbl_day_no_fuquan
(
   stock_id
);

create index IDX_DAY_NO_FUQUAN_2 on tbl_day_no_fuquan
(
   pub_date
);
