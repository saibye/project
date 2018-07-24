
drop table if exists tbl_fupai;

/*==============================================================*/
/* Table: tbl_fupai                                               */
/*==============================================================*/
create table tbl_fupai
(
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   fupai_date           date not null,
   tingpai_date         date not null,
   days                 int,
   inst_date            date,
   inst_time            time,
   up_date              date,
   primary key (stock_id, stock_loc, fupai_date)
);

/*==============================================================*/
/* Index: IDX_TBL_FUPAI_1                                       */
/*==============================================================*/
create index IDX_TBL_FUPAI_1 on tbl_fupai
(
   stock_id
);

