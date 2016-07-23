drop table if exists tbl_30min;

/*==============================================================*/
/* Table: tbl_30min                                             */
/*==============================================================*/
create table tbl_30min
(
   pub_date             date not null,
   pub_time             time not null,
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
   ema26                float,
   ema12                float,
   diff                 float,
   dea                  float,
   macd                 float,
   inst_date            date not null,
   inst_time            time not null,
   rsv1                 float,
   rsv2                 float,
   rsv3                 float,
   primary key (pub_date, pub_time, stock_id, stock_loc)
);

-- ALTER TABLE tbl_30min ADD macd float;


