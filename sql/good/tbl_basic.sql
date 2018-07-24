drop table if exists tbl_basic;

/*==============================================================*/
/* Table: tbl_basic                                             */
/*==============================================================*/
create table tbl_basic
(
   stock_id             char(8) not null,
   stock_name           varchar(20),
   industry             varchar(20),
   area                 varchar(20),
   pe                   float,
   outstanding          float,
   totals               float,
   total_assets         float,
   liquid_assets        float,
   fixed_assets         float,
   reserved             float,
   reserved_per         float,
   eps                  float,
   bvps                 float,
   pb                   float,
   time_to_market       varchar(10),
   inst_date            date not null,
   inst_time            time not null,
   primary key (stock_id)
);

create index IDX_TBL_BASIC_1 on tbl_watch
(  
   stock_id
);

