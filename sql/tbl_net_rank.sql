drop table if exists tbl_net_rank;

/*==============================================================*/
/* Table: tbl_net_rank                                          */
/*==============================================================*/
create table tbl_net_rank
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   watcher              char(8) not null,
   open_price           float,
   close_price          float,
   net1                 float,
   net200               float,
   net400               float,
   net800               float,
   net1000              float,
   net2000              float,
   net3000              float,
   rank                 float,
   buy_ma5              float,
   buy_ma5_date         date,
   buy_ma10             float,
   buy_ma10_date        date,
   buy1                 float,
   buy200               float,
   buy400               float,
   buy800               float,
   buy1000              float,
   buy2000              float,
   buy3000              float,
   sell1                float,
   sell200              float,
   sell400              float,
   sell800              float,
   sell1000             float,
   sell2000             float,
   sell3000             float,
   inst_date            date not null,
   inst_time            time not null,
   primary key (pub_date, stock_id, stock_loc, watcher)
);

