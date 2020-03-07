
create table tbl_lihua_day
(
   pub_date            date not null,
   close_price         float,
   deal_price          float,
   action              varchar(20),
   position            varchar(20),
   primary key (pub_date)
);
