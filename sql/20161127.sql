
--

--where a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x order by pub_date desc limit 14) y)

--
+----------+------------+------------+-------------+-------+-------+-------+-------+-------+-------+------+-------+-------+
| stock_id | pub_date   | open_price | close_price | ma5   | ma10  | ma20  | ma30  | ma60  | ma150 | macd | diff  | dea   |
+----------+------------+------------+-------------+-------+-------+-------+-------+-------+-------+------+-------+-------+
| 002678   | 2016-10-24 |      13.19 |       13.56 | 13.32 | 13.37 | 13.34 | 13.42 | 13.47 | 12.75 | 0.01 | -0.02 | -0.03 |
+----------+------------+------------+-------------+-------+-------+-------+-------+-------+-------+------+-------+-------+
--

and a.stock_id='002678'

and (a.close_price-a.open_price) / a.last_close_price * 100 <= 5
and a.pub_date='2016-10-24'
-- 当日成交量放大，翻倍
-- 次日高开，收阳线
-- 次日成交量放大
-- 之前几日横盘

select a.stock_id, a.pub_date, a.open_price, a.close_price,
       a.last_close_price last, a.deal_total_count total,
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.pub_date='2016-11-14'
and a.close_price > a.open_price
and b.ma5   >= a.open_price
and b.ma10  >= a.open_price
and b.ma20  >= a.open_price
and b.ma30  >= a.open_price
and b.ma60  >= a.open_price
and b.ma5   <= a.close_price
and b.ma10  <= a.close_price
and b.ma20  <= a.close_price
and b.ma30  <= a.close_price
and b.ma60  <= a.close_price
and b.ma150 <= a.close_price
and b.macd >= -0.01
and b.diff >= -0.02
and b.dea  >= -0.03
order by 2 desc,1


--
下一个交易日

select * from (select distinct pub_date from tbl_day_tech x where pub_date > '2016-11-14' order by pub_date limit 1) y

a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x where pub_date <= '' order by pub_date desc limit 14) y)

select * from (select distinct pub_date from tbl_day_tech x 
            where pub_date <= (select distinct pub_date from tbl_day_tech z where pub_date > '2016-11-14' order by pub_date limit 1)
            order by pub_date desc limit 5) y

a.pub_date in ( select * from (select distinct pub_date from tbl_day_tech x 
where pub_date <= (select distinct pub_date from tbl_day_tech z where pub_date > '2016-11-14' order by pub_date limit 1)
order by pub_date desc limit 5) y)


-- list
select a.stock_id from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.pub_date='2016-11-14'
and a.close_price > a.open_price
and b.ma5   >= a.open_price
and b.ma10  >= a.open_price
and b.ma20  >= a.open_price
and b.ma30  >= a.open_price
and b.ma60  >= a.open_price
and b.ma5   <= a.close_price
and b.ma10  <= a.close_price
and b.ma20  <= a.close_price
and b.ma30  <= a.close_price
and b.ma60  <= a.close_price
and b.ma150 <= a.close_price
and b.macd >= -0.01
and b.diff >= -0.02
and b.dea  >= -0.03


-- detail
select a.stock_id, a.pub_date, a.open_price, a.close_price,
       a.last_close_price last, a.deal_total_count total,
       b.ma5, b.ma10, b.ma20, b.ma30, b.ma60, b.ma150,
       macd, diff, dea
from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.pub_date in (select * from (select distinct pub_date from tbl_day_tech x
where pub_date <= (select distinct pub_date from tbl_day_tech z where pub_date > '2016-11-14' order by pub_date limit 1)
order by pub_date desc limit 5) y)
and a.stock_id in (select * from ( select a.stock_id from tbl_day a, tbl_day_tech b
where a.stock_id=b.stock_id
and a.pub_date=b.pub_date
and a.pub_date='2016-11-14'
and a.close_price > a.open_price
and b.ma5   >= a.open_price
and b.ma10  >= a.open_price
and b.ma20  >= a.open_price
and b.ma30  >= a.open_price
and b.ma60  >= a.open_price
and b.ma5   <= a.close_price
and b.ma10  <= a.close_price
and b.ma20  <= a.close_price
and b.ma30  <= a.close_price
and b.ma60  <= a.close_price
and b.ma150 <= a.close_price
and b.macd >= -0.01
and b.diff >= -0.02
and b.dea  >= -0.03) c)
order by 1, 2 desc


-- 
select max(pub_date) from tbl_day_tech
select distinct pub_date from tbl_day_tech z where pub_date < (select max(pub_date) from tbl_day_tech) order by pub_date desc limit 1
select distinct pub_date from tbl_day_tech z where pub_date < (select max(pub_date) from tbl_day_tech where pub_date <= '20161123') order by pub_date desc limit 1


