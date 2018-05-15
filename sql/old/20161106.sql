--

-- 
desc tbl_day


--
select a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150
from tbl_day a, tbl_day_tech b
where a.stock_id = '002780'
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date


select a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150
from tbl_day a, tbl_day_tech b
where a.stock_id = '002780'
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.open_price < a.close_price
and b.ma5   > a.open_price
and b.ma10  > a.open_price
and b.ma20  > a.open_price
and b.ma30  > a.open_price
and b.ma60  > a.open_price
and b.ma150 > a.open_price
and b.ma5   < a.close_price
and b.ma10  < a.close_price
and b.ma20  < a.close_price
and b.ma30  < a.close_price
and b.ma60  < a.close_price
and b.ma150 < a.close_price



select stock_id, count(1) from tbl_day_tech
group by stock_id
order by 1


select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date >= '2016-09-28'
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.open_price < a.close_price
and b.ma5   > a.open_price
and b.ma10  > a.open_price
and b.ma20  > a.open_price
and b.ma30  > a.open_price
and b.ma60  > a.open_price
and b.ma150 > a.open_price
and b.ma5   < a.close_price
and b.ma10  < a.close_price
and b.ma20  < a.close_price
and b.ma30  < a.close_price
and b.ma60  < a.close_price
and b.ma150 < a.close_price
order by 1,2


-- strictly!
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date >= '2016-09-01'
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.open_price < a.close_price
and b.ma5   > a.open_price
and b.ma10  > a.open_price
and b.ma20  > a.open_price
and b.ma30  > a.open_price
and b.ma60  > a.open_price
and b.ma150 > a.open_price
and b.ma5   < a.close_price
and b.ma10  < a.close_price
and b.ma20  < a.close_price
and b.ma30  < a.close_price
and b.ma60  < a.close_price
and b.ma150 < a.close_price
and b.macd > 0
and b.diff > 0
and b.dea  >= 0
order by 2,1











-- sql
