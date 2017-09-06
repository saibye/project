


select pub_date, count(1) from tbl_top_list
group by pub_date
order by 1;


--



select pub_date, stock_id, 
       open_price, high_price, close_price, low_price,
       last_close_price, deal_total_count,
       round((close_price - last_close_price)/last_close_price*100, 2) rt
from tbl_day
where stock_id = '002300'
and pub_date <= '2017-02-11'
order by pub_date desc limit 10

/

-- 振幅超过19
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date like '2016%'
and (high_price - low_price) / last_close_price * 100 >= 19
order by pub_date


-- 振幅超过17
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date  >= '2016-02-01'
and (high_price - low_price) / last_close_price * 100 >= 17
order by pub_date



-- 振幅超过17，开盘跌停
-- done, good, to implement
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date  >= '2016-02-01'
and (high_price - low_price) / last_close_price * 100 >= 17
and (open_price - low_price) / last_close_price * 100 < 0.5
order by pub_date


-- 振幅超过17，收盘涨停
-- done
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date  >= '2016-02-01'
and (high_price - low_price) / last_close_price * 100 >= 17
and (high_price - close_price) / last_close_price * 100 < 0.5
order by pub_date

-- 振幅超过17，收盘涨停
-- for 002346
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date  >= '2016-02-01'
and (high_price - low_price) / last_close_price * 100 >= 17
and (high_price - close_price) / last_close_price * 100 < 0.1
and (open_price - low_price) / last_close_price * 100 < 3.5
order by pub_date



-- 振幅超过17, else
-- else
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date  >= '2016-02-01'
and (high_price - low_price) / last_close_price * 100 >= 17
and (open_price - low_price) / last_close_price * 100 >= 1
and (high_price - close_price) / last_close_price * 100>=1
order by pub_date


+++均线压制，ma5-ma60
一阳三线
macd全为正
放量涨停，量比4+

select a.stock_id, a.pub_date, a.open_price, a.close_price,
       a.last_close_price last, a.deal_total_count total,
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.stock_id = '601003'
and a.pub_date = '2016-11-21'


--and a.pub_date='2016-11-21'

select a.stock_id, a.pub_date, a.open_price, a.close_price,
       a.last_close_price last, a.deal_total_count total,
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.close_price > a.open_price
and (a.close_price - a.last_close_price) / a.last_close_price * 100 > 9.8
and b.ma5   >= a.open_price
and b.ma10  >= a.open_price
and b.ma20  >= a.open_price
and b.ma5   <= a.close_price
and b.ma10  <= a.close_price
and b.ma20  <= a.close_price
and b.ma5   >  b.ma10
and b.ma10  >  b.ma20
and b.ma20  >  b.ma30
and b.ma30  >  b.ma60
and b.macd >= 0.00
and b.diff >= 0.01
and b.dea  >= 0.01
order by 2, 1


-- recent
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last
from tbl_day
where pub_date in (select * from (select distinct pub_date from tbl_day where pub_date <= '2017-02-01' order by pub_date desc limit 30) x)
and (high_price - low_price) / last_close_price * 100 >= 17
and (open_price - low_price) / last_close_price * 100 < 0.5
order by pub_date




select distinct stock_id from tbl_day where pub_date=(select max(pub_date) from tbl_day) order by 1





# 20170131.sql
