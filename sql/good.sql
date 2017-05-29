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
select stock_id, round((close_price-last_close_price)/last_close_price*100, 3) rate
from tbl_day
where pub_date = '2017-04-14' 
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

-- 
select distinct pub_date from tbl_day
where pub_date >= '2017-01-03'
order by pub_date limit 10;


select round((close_price/last_close_price - 1)*100, 2) rate
from tbl_day
where stock_id='601375'
and pub_date='2017-04-20'
and last_close_price > 0;


select str_to_date('20170423', '%Y%m%d');

select date_format('2017-04-23', '%Y%m%d');

select date_add('2017-04-23', interval -1 day);
select date_add('20170423', interval -1 day);


select str_to_date(time_to_market, '%Y%m%d') from tbl_basic
where time_to_market like '201703%';

-- 
select stock_id, stock_name, industry, area, time_to_market
from tbl_basic
where  str_to_date(time_to_market, '%Y%m%d') >= date_add('20170423', interval -60 day);

-- 上市天数
select datediff('2017-04-23', str_to_date(time_to_market, '%Y%m%d')) days
from tbl_basic
where  stock_id = '601375';

--
select pub_date, (sum(buy1)-sum(sell1))/10000 N1, sum(buy1)/10000 B1, sum(sell1)/10000 S1, sum(mid1)/10000 M1
from tbl_tick_sum
where pub_date <='2017-05-07'
group by pub_date
order by 1 desc limit 5;


select (sum(buy1)-sum(sell1))/10000 N1, sum(buy1)/10000 B1, sum(sell1)/10000 S1, sum(mid1)/10000 M1,
(sum(buy1000)-sum(sell1000))/10000 N2, sum(buy1000)/10000 B2, sum(sell1000)/10000 S2, sum(mid1000)/10000 M2,
(sum(buy3000)-sum(sell3000))/10000 N3, sum(buy3000)/10000 B3, sum(sell3000)/10000 S3, sum(mid3000)/10000 M3,
(sum(buy10000)-sum(sell10000))/10000 N4, sum(buy10000)/10000 B4, sum(sell10000)/10000 S4, sum(mid10000)/10000 M4
from tbl_tick_sum
where pub_date ='2017-05-05'

-- 按市值
select a.stock_id, a.pub_date, b.stock_name, a.close_price, b.outstanding,
       a.close_price * b.outstanding liq, a.close_price * b.totals
from tbl_day a, tbl_basic b
where a.stock_id = b.stock_id
and a.pub_date = (select * from (select max(pub_date) from tbl_day) t)
order by liq desc limit 100



select c.pub_date, (sum(buy1)-sum(sell1))/10000 N1, sum(buy1)/10000 B1, sum(sell1)/10000 S1, sum(mid1)/10000 M1
from (
    select a.stock_id stock_id, a.pub_date, b.stock_name, b.time_to_market,  a.close_price, b.outstanding,
           a.close_price * b.outstanding liq, a.close_price * b.totals total
    from tbl_day a, tbl_basic b
    where a.stock_id = b.stock_id
    and a.pub_date = (select * from (select max(pub_date) from tbl_day) t1)
) t2, tbl_tick_sum c
where t2.stock_id = c.stock_id
and c.pub_date='2017-05-05'
and t2.liq <= 100


select * from tbl_name where inst_date='2017-05-29'





# good.sql
