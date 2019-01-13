
drop table if exists tbl_day_today;

/*==============================================================*/
/* Table: tbl_day_today                                               */
/*==============================================================*/
create table tbl_day_today
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   changepercent        float,
   deal_total_count     float,
   deal_total_amount    float,
   turnoverratio        float,
   per                  float,
   pb                   float,
   mktcap               float,
   nmc                  float,
   inst_date            date,
   inst_time            time,
   primary key (pub_date, stock_id)
);

/*==============================================================*/
/* Index: IDX_TBL_DAY_TODAY_1                                   */
/*==============================================================*/
create index IDX_TBL_DAY_TODAY_1 on tbl_day_today ( stock_id);

create index IDX_TBL_DAY_TODAY_2 on tbl_day_today ( pub_date);

