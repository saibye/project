
--

select pub_date, close_price, open_price, low_price, high_price, last_close_price, deal_total_count
from tbl_day
where stock_id='600466'
and pub_date <= '2016-10-28'
order by pub_date desc
limit 2;




select a.close_price, a.open_price, a.low_price, a.high_price, a.last_close_price, b.ma5, b.ma10
from tbl_day a, tbl_day_tech b
where a.stock_id='600466'
and a.pub_date  = '2016-10-28'
and a.stock_id  = b.stock_id
and a.pub_date  = b.pub_date;




--
select count(1) from tbl_day 
where stock_id = '600857'
and pub_date > '2016-09-29'
and close_price > 14.57
order by pub_date 
limit 10;



select * from tbl_day 
where stock_id = '600857'
and pub_date > '2016-09-29'
order by pub_date 
limit 10;


select count(1) from 
(select * from tbl_day 
where stock_id = '600857'
and pub_date > '2016-09-29'
order by pub_date 
limit 10) t1
where close_price > 14.57


select count(1) from 
(select * from tbl_day 
where stock_id = '600868'
and pub_date > '2016-09-28'
order by pub_date 
limit 10) t1
where close_price > 5.31



select count(1) from 
(select * from tbl_day 
where stock_id = '600868'
and pub_date > '2016-09-28'
order by pub_date 
limit 10) t1
where low_price > 5.10



--a.stock_id  = '603066'
--and   a.pub_date >= '2016-06-01'

select pub_date, deal_total_count 
from tbl_day a
where a.stock_id  = '603066'
and   a.pub_date >= '2016-06-01''
and deal_total_count = 
(select min(deal_total_count) from tbl_day b
where b.pub_date >= '2016-06-01'
and   a.stock_id  = b.stock_id
)
;


--
select min(pub_date) from (
select pub_date from tbl_day
where stock_id = '603066'
order by pub_date desc
limit 60
) t1



--
select pub_date, deal_total_count 
from tbl_day a
where a.stock_id = '603066'
and a.pub_date >= (select min(pub_date) from (
    select pub_date from tbl_day
    where stock_id = '603066'
    order by pub_date desc
    limit 60) t1)
and deal_total_count = (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from (
        select pub_date from tbl_day
        where stock_id = '603066'
        order by pub_date desc limit 60) t1)
    )
;

--
最近3(n1)天的最小成交量，是最近60(n2)天的最小成交量
--
select pub_date, deal_total_count 
from tbl_day a
where a.stock_id = '603066'
and a.pub_date >= (select min(pub_date) from ( select pub_date from tbl_day where stock_id = '603066' order by pub_date desc limit 50) t1)
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


--
select pub_date, deal_total_count 
from tbl_day a
where a.stock_id = '603066'
and a.pub_date >= (select min(pub_date) from 
        ( select pub_date from tbl_day 
          where stock_id = '603066' 
          order by pub_date desc limit 50) t1)
and deal_total_count = 
    (select min(deal_total_count) 
     from tbl_day b where b.stock_id = '603066' 
     and b.pub_date >= (select min(pub_date) from 
         ( select pub_date from tbl_day 
           where stock_id = '603066' 
           order by pub_date desc limit 50) t1))
and (select min(deal_total_count) from tbl_day b
    where b.stock_id = '603066'
    and b.pub_date >= (select min(pub_date) from 
        ( select pub_date from tbl_day 
          where stock_id = '603066' 
          order by pub_date desc limit 50) t1)) = 
    (select min(deal_total_count) from tbl_day b 
     where b.stock_id = '603066' 
     and b.pub_date >= (select min(pub_date) from 
         ( select pub_date from tbl_day 
           where stock_id = '603066' 
           order by pub_date desc limit 150) t1)) 
order by pub_date desc
limit 1;

-- 
select pub_date, open_price, close_price, deal_total_count 
from tbl_day a
where a.stock_id  = '603066'
and   a.pub_date >= '2016-09-14'
order by pub_date
limit 3;


-- 

select distinct stock_id from tbl_day
where pub_date = (select max(pub_date) from tbl_day)

-----------------------------------------------------------------
2016-12-4

select pub_date, deal_total_count 
from tbl_day a
where a.stock_id  = '600608'
and   a.pub_date >= '2016-08-01'
and deal_total_count = 
(select min(deal_total_count) from tbl_day b
where b.pub_date >= '2016-08-01'
and   a.stock_id  = b.stock_id
)
;
-- 2016-09-29


SELECT min(pub_date)
FROM
(SELECT pub_date FROM tbl_day
WHERE stock_id = '600608' ORDER BY
pub_date DESC LIMIT 10) t1;

SELECT min(pub_date)
FROM
(SELECT pub_date FROM tbl_day
WHERE stock_id = '600608' ORDER BY
pub_date DESC LIMIT 30) t1;
-- 2016-08-02


-- back ma5
select a.pub_date event_date, a.stock_id, b.pub_date back_date,
       a.v1, a.v2, a.v4
from tbl_good a, tbl_day b, tbl_day_tech c
where a.stock_id = b.stock_id
and   b.stock_id = c.stock_id
and   b.pub_date = c.pub_date
and   (b.close_price <= c.ma5  or (c.ma10<= b.high_price and c.ma10 >= b.low_price))
and   a.good_type = 'dadan2'
and   b.pub_date = '2016-11-29';














