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

--  601375
select a.pub_date event_date, a.stock_id, b.pub_date back_date,
       a.v1 volume, a.v2 price, a.v4 time 
       from tbl_good a, tbl_day b, tbl_day_tech c 
       where a.stock_id = b.stock_id 
       and   b.stock_id = c.stock_id 
       and   b.pub_date = c.pub_date 
       and   b.pub_date>= a.pub_date
       and  (c.ma20<= b.high_price and c.ma20 >= b.low_price)
       and   a.good_type = 'dadan3' and   b.pub_date  = '2017-03-15'
       and   a.pub_date in 
        (select * from (select distinct pub_date from tbl_good d where d.pub_date <= '2017-03-15' order by pub_date desc limit 10) x)


select pub_date, stock_id, pchange, amount, buy, sell, reason
from tbl_top_list
where pub_date >= '2017-04-01'
order by pub_date, stock_id;


--  2017-4-10
select stock_id, round((close_price-open_price)/last_close_price*100, 3) rate
from tbl_day
where pub_date = '2017-01-03' 
and (close_price - last_close_price) / last_close_price * 100 >= 9.8
order by stock_id

select pub_date,
       open_price open, close_price close, low_price low, high_price high, 
       last_close_price last, deal_total_count vol,
       round((close_price-open_price)/last_close_price*100,2) rate,
       round((high_price - low_price)/last_close_price*100,2) amp,
       round((open_price - low_price)/last_close_price*100,2) dis
from tbl_day
where stock_id = '600698'
and pub_date <= '2017-01-03'
order by pub_date desc limit 100




# good.sql
