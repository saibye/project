# good.sql

-- 002584
select stock_id, pub_date,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last, deal_total_count vol
from tbl_day
where pub_date in (select * from (select distinct pub_date from tbl_day where pub_date <= '2017-03-11' order by pub_date desc limit 60) x)
and (high_price - last_close_price) / last_close_price * 100 >= 4
and (low_price  - last_close_price) / last_close_price * 100 <= -7
and (open_price - low_price) / last_close_price * 100 < 0.5
order by pub_date










# good.sql
