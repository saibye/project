
--

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


