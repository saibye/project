drop table if exists tbl_day_no_fuquan;

/*==============================================================*/
/* Table: tbl_day_no_fuquan                                     */
/*==============================================================*/
create table tbl_day_no_fuquan
(
   pub_date             date not null,
   stock_id             char(8) not null,
   open_price           float,
   high_price           float,
   close_price          float,
   low_price            float,
   last_close_price     float,
   deal_total_count     float,
   deal_total_amount    double,
   inst_date            date not null,
   inst_time            time not null,
   primary key (pub_date, stock_id)
);

<<<<<<< HEAD

/*==============================================================*/
/* Index: IDX_TBL_DAY_1                                         */
/*==============================================================*/
create index IDX_TBL_DAY_NOFQ_1 on tbl_day_no_fuquan
=======
/*==============================================================*/
/* Index: IDX_DAY_NO_FUQUAN_1                                   */
/*==============================================================*/
create index IDX_DAY_NO_FUQUAN_1 on tbl_day_no_fuquan
>>>>>>> 5fe7f44febec12bbbb98624bc5dd1bf2b0b7c9bc
(
   stock_id
);

<<<<<<< HEAD
create index IDX_TBL_DAY_NOFQ_2 on tbl_day_no_fuquan
(
   pub_date
);

=======
/*==============================================================*/
/* Index: IDX_DAY_NO_FUQUAN_2                                   */
/*==============================================================*/
create index IDX_DAY_NO_FUQUAN_2 on tbl_day_no_fuquan
(
   pub_date
);
>>>>>>> 5fe7f44febec12bbbb98624bc5dd1bf2b0b7c9bc
