
drop table if exists t_trc_image;

create table t_trc_image
(
   stock_id             char(8) not null,
   pub_date             char(10) not null,
   media_id             varchar(128),
   created              int,
   primary key (stock_id, pub_date)
);

create index IDX_T_TRC_IMAGE_1 on t_trc_image
(
   stock_id,
   pub_date
);

