drop table if exists tbl_xsg;

create table tbl_xsg
(
   stock_id             char(8) not null,
   free_date            date not null,
   free_count           float not null,
   ratio                float not null,
   inst_date            date not null,
   inst_time            time not null,
   primary key (stock_id, free_date)
);

create index IDX_XSG_1 on tbl_xsg(stock_id);
