drop index IDX_TOP_LIST_1 on tbl_top_list;

drop table if exists tbl_top_list;

create table tbl_top_list
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   stock_name           varchar(20),
   pchange              float,
   amount               float,
   buy                  float,
   bratio               float,
   sell                 float,
   sratio               float,
   reason               varchar(100) not null,
   inst_date            date not null,
   inst_time            time not null,
   rsv1                 float,
   rsv2                 float,
   rsv3                 float,
   primary key (pub_date, stock_id, stock_loc, reason)
);

create index IDX_TOP_LIST_1 on tbl_top_list
(
   stock_id
);

create index IDX_TOP_LIST_2 on tbl_top_list
(
   pub_date
);
