--

-- 
desc tbl_day

--
select distinct pub_date from tbl_day_tech x order by pub_date desc limit 30


select pub_date, count(1) from tbl_day
group by pub_date
order by pub_date;

-- cross5
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 14) y)
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.open_price < a.close_price
and b.ma5   > a.open_price
and b.ma10  > a.open_price
and b.ma20  > a.open_price
and b.ma30  > a.open_price
and b.ma60  > a.open_price
and b.ma5   < a.close_price
and b.ma10  < a.close_price
and b.ma20  < a.close_price
and b.ma30  < a.close_price
and b.ma60  < a.close_price
and b.macd > 0
and b.diff > 0
and b.dea  >= 0
order by 2 desc,1


--
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30
from tbl_day a, tbl_day_tech b
where 1=1
and a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.stock_id='000002'
order by a.pub_date


--


day1: open  > close and rate > 5%
day2: close > open  and rate > 5% and open < ref(low) and close >= ref(open)













-- test
select a.stock_id, a.pub_date, a.open_price, a.close_price, 
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 14) y)
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
and b.macd >= -0.01
and b.diff >= -0.02
and b.dea  >= -0.02
order by 2 desc,1









-- sql
