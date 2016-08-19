drop table if exists tbl_day_orig;

/*==============================================================*/
/* Table: tbl_day_orig                                          */
/*==============================================================*/
create table tbl_day_orig
(
   pub_date             date not null,
   pub_time             time,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   price_change         float,
   change_rate          float,
   deal_total_count     float,
   deal_total_amount    double,
   ma5                  float,
   ma10                 float,
   ma20                 float,
   ma30                 float,
   ma60                 float,
   vma5                 float,
   vma10                float,
   vma20                float,
   turnover             float,
   ema12                float,
   ema26                float,
   diff                 float,
   dea                  float,
   macd                 float,
   inst_date            date not null,
   inst_time            time not null,
   primary key (pub_date, stock_id, stock_loc)
);

