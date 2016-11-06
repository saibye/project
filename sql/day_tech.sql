drop index IDX_DAY_TECH_1 on tbl_day_tech;

drop table if exists tbl_day_tech;

/*==============================================================*/
/* Table: tbl_day_tech                                          */
/*==============================================================*/
create table tbl_day_tech
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   close_price          float,
   price_change         float,
   change_rate          float,
   ma5                  float,
   ma10                 float,
   ma20                 float,
   ma30                 float,
   ma60                 float,
   ma120                float,
   ma150                float,
   vma5                 float,
   vma10                float,
   vma20                float,
   turnover             float,
   ema12                float,
   ema26                float,
   diff                 float,
   dea                  float,
   macd                 float,
   upper                float,
   ene                  float,
   lower                float,
   inst_date            date,
   inst_time            time,
   primary key (pub_date, stock_id, stock_loc)
);

/*==============================================================*/
/* Index: IDX_DAY_TECH_1                                        */
/*==============================================================*/
create index IDX_DAY_TECH_1 on tbl_day_tech
(
   stock_id
);

