drop table if exists tbl_good;

/*==============================================================*/
/* Table: tbl_good                                              */
/*==============================================================*/
create table tbl_good
(
   pub_date             date not null,
   stock_id             char(8) not null,
   stock_loc            char(2) not null,
   holder               char(8) not null,
   good_type            char(10) not null,
   good_reason          varchar(64),
   v1                   float,
   v2                   float,
   v3                   float,
   v4                   char(10),
   buy_price            float,
   buy_date             date,
   sell_price           float,
   sell_date            date,
   changed              float,
   is_valid             int not null,
   inst_date            date,
   inst_time            time,
   upd_date             date,
   upd_time             time,
   primary key (pub_date, stock_id, stock_loc, holder, good_type)
);

