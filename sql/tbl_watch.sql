
drop table if exists tbl_watch;

/*==============================================================*/
/* Table: tbl_watch                                               */
/*==============================================================*/
create table tbl_watch
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   good_type            char(30) not null,
   expect_price         float,
   expect_direction     char(2),
   title                varchar(64),
   message              varchar(4096),
   inst_date            date,
   inst_time            time,
   primary key (pub_date, stock_id, stock_loc, good_type)
);

/*==============================================================*/
/* Index: IDX_TBL_WATCH_1                                       */
/*==============================================================*/
create index IDX_TBL_WATCH_1 on tbl_watch
(
   stock_id
);

create index IDX_TBL_WATCH_2 on tbl_watch
(
   pub_date
);

