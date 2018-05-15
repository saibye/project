
--

select pub_date, close_price, open_price, low_price, high_price, last_close_price, deal_total_count
from tbl_day
where stock_id='600466'
and pub_date <= '2016-12-28'
order by pub_date desc
limit 10;




--
最近3(n1)天的最小成交量，是最近60(n2)天的最小成交量
--
select pub_date, deal_total_count 
from tbl_day a
where a.stock_id = '000757'
and a.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757'  order by pub_date desc limit 50) t1)
and deal_total_count
    = 
    (select min(deal_total_count) from tbl_day b where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 50) t1))
and (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 50) t1))
    = 
    (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 150) t1)) 
order by pub_date desc
limit 1;



--今天的成交量，是最近60天最近成交量
select pub_date, deal_total_count 
from tbl_day a
where a.stock_id = '000757'
and a.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757'  order by pub_date desc limit 50) t1)
and deal_total_count
    = 
    (select min(deal_total_count) from tbl_day b where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 50) t1))
and (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 50) t1))
    = 
    (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 150) t1)) 
order by pub_date desc
limit 1;



select min(deal_total_count) from tbl_day b 
where b.stock_id  = '000757'
and   b.pub_date <= '2016-09-27'

--
select stock_id, pub_date, deal_total_count from tbl_day a
where stock_id = '000757'
and   pub_date = '2016-09-27'
and (select min(deal_total_count) from tbl_day b 
where b.stock_id  = '000757'
and   b.pub_date <= '2016-09-27'
and   b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757' order by pub_date desc limit 60) t1))
=
(select min(deal_total_count) from tbl_day b
where b.stock_id  = '000757'
and   b.pub_date  = '2016-09-27')

select stock_id, pub_date, deal_total_count from tbl_day a
where stock_id = '000757'
and   pub_date = '2016-09-27'
and (select min(deal_total_count) from tbl_day b 
where b.stock_id  = '000757'
and   b.pub_date <= '2016-09-27'
and   b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757' and pub_date <= '2016-09-27' order by pub_date desc limit 60) t1))
=
(select min(deal_total_count) from tbl_day c
where c.stock_id  = '000757'
and   c.pub_date  = '2016-09-27')




select stock_id, pub_date, deal_total_count from tbl_day a
where stock_id = '000757'
and   pub_date = '2016-09-27'
and (select min(deal_total_count) from tbl_day b 
where b.stock_id  = '000757'
and   b.pub_date <= a.pub_date
and   b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757' and pub_date <= '2016-09-27' order by pub_date desc limit 60) t1))
=
(select min(deal_total_count) from tbl_day c
where c.stock_id  = '000757'
and   c.pub_date  = a.pub_date)



select stock_id, pub_date, deal_total_count from tbl_day a
where stock_id = '000757'
and   pub_date = '2016-09-27'
and (select min(deal_total_count) from tbl_day b 
where b.stock_id  = a.stock_id
and   b.pub_date <= a.pub_date
and   b.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '000757' and pub_date <= '2016-09-27' order by pub_date desc limit 60) t1))
=
(select min(deal_total_count) from tbl_day c
where c.stock_id  = a.stock_id
and   c.pub_date  = a.pub_date)


--
