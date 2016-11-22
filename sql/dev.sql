
select pub_date, count(1) 
from tbl_day
group by pub_date
order by 1


--

desc tbl_day

-- 
select distinct a.stock_id
from tbl_day a, tbl_day_tech b
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 10) y)
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
order by 1

-- recent detail
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 10) y)
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.stock_id='000002'
order by 2 desc,1


--
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x where pub_date <='20160802' order by pub_date desc limit 10) y)
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.stock_id='000002'
order by 2 desc,1


day1: open  > close and rate > 5%
day2: close > open  and rate > 5% and open < ref(low) and close >= ref(open)


select distinct pub_date from tbl_day_tech x where pub_date <='2016-11-21' order by pub_date desc limit 30


--

