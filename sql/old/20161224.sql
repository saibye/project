
--
update tbl_net_rank set net1=net1/10, 
       net200 = net200 / 10,
       net400 = net400 / 10,
       net800 = net800 / 10,
       net1000= net1000/ 10,
       net2000= net2000/ 10,
       net3000= net3000/ 10,
       buy1   = buy1   / 10,
       buy200 = buy200 / 10,
       buy400 = buy400 / 10,
       buy800 = buy800 / 10,
       buy1000= buy1000/ 10,
       buy2000= buy2000/ 10,
       buy3000= buy3000/ 10,
       sell1   = sell1   / 10,
       sell200 = sell200 / 10,
       sell400 = sell400 / 10,
       sell800 = sell800 / 10,
       sell1000= sell1000/ 10,
       sell2000= sell2000/ 10,
       sell3000= sell3000/ 10;


--
alter table tbl_net_rank drop column buy_ma5;

alter table tbl_net_rank change buy_ma5       subject           varchar(30);
alter table tbl_net_rank change buy_ma5_date  cata              char(4);
alter table tbl_net_rank change buy_ma10      rate              float;
alter table tbl_net_rank change buy_ma10_date last_close_price  float;

alter table tbl_net_rank drop column last_close_price;

alter table tbl_net_rank add  column message varchar(512);

--

delete from tbl_net_rank where pub_date='2016-12-23';


--

update tbl_net_rank set subject = '吸筹', cata='0', rate='0' where pub_date <='2016-12-22';

--
create index IDX_TBL_NET_RANK_1 on tbl_net_rank ( stock_id);


--
select (close_price-last_close_price)/last_close_price *100 from tbl_day
where stock_id = '000672';

"""
update tbl_net_rank set rate='0'
from tbl_net_rank a, tbl_day b
where a.pub_date <='2016-12-22'
and a.stock_id = '000672'
and a.pub_date = b.pub_date
and a.stock_id = b.stock_id;
"""

--
select * from tbl_net_rank
where stock_id='000672'
order by pub_date desc
limit 5;


--
select a.pub_date event_date, a.stock_id, b.pub_date back_date, a.v1 volume, a.v2 price, a.v4 time 
from tbl_good a, tbl_day b, tbl_day_tech c 
where a.stock_id = b.stock_id 
and   b.stock_id = c.stock_id 
and   b.pub_date = c.pub_date 
and   (b.close_price <= c.ma5  or (c.ma10<= b.high_price and c.ma10 >= b.low_price)) 
and   a.good_type = 'dadan2' 
and   b.pub_date  = '2016-11-29'

--
select distinct pub_date from tbl_good order by pub_date desc limit 5


--
select a.pub_date event_date, a.stock_id, b.pub_date back_date, a.v1 volume, a.v2 price, a.v4 time 
from tbl_good a, tbl_day b, tbl_day_tech c 
where a.stock_id = b.stock_id 
and   b.stock_id = c.stock_id 
and   b.pub_date = c.pub_date 
and   (b.close_price <= c.ma5  or (c.ma10<= b.high_price and c.ma10 >= b.low_price)) 
and   a.good_type = 'dadan3' 
and   b.pub_date  = '2016-12-21'
and   a.pub_date in (select * from (select distinct pub_date from tbl_good order by pub_date desc limit 10) x)


--
insert into tbl_fupai (
stock_id, stock_loc, fupai_date, tingpai_date, days,
inst_date, inst_time)
values ('000757', 'cn', '2016-09-27', '2016-03-27', 180, '2016-12-25', '09:41:00');

--
select * from tbl_fupai
where stock_id = '000757'
order by fupai_date desc limit 1


