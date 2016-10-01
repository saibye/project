drop table if exists tbl_real_trade;

/*==============================================================*/
/* Table: tbl_real_trade                                        */
/*==============================================================*/
create table tbl_real_trade
(
   buy_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   holder               char(8) not null,
   buy_price            float not null,
   sell_price           float,
   changed              float,
   sell_date            date,
   is_valid             int not null,
   buy_reason           varchar(256),
   inst_date            date not null,
   inst_time            time not null,
   primary key (buy_date, stock_id, stock_loc, holder)
);

