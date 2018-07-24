drop table if exists tbl_tick_sum;

/*==============================================================*/
/* Table: tbl_tick_sum                                          */
/*==============================================================*/
create table tbl_tick_sum
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   buy1                 float,
   sell1                float,
   mid1                 float,
   buy1000              float,
   sell1000             float,
   mid1000              float,
   buy3000              float,
   sell3000             float,
   mid3000              float,
   buy10000             float,
   sell10000            float,
   mid10000             float,
   inst_date            date not null,
   inst_time            time not null,
   primary key (pub_date, stock_id, stock_loc)
);

create index IDX_TBL_TICK_SUM_1 on tbl_tick_sum(stock_id);
create index IDX_TBL_TICK_SUM_2 on tbl_tick_sum(pub_date);

