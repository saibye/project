
--
--  涨停；最低点，跌停

--
--  从跌停到涨停 

select * from tbl_day
where pub_date = '2016-12-26' 
and (close_price - last_close_price) / last_close_price * 100 >= 9.8 


select * from tbl_day
where pub_date = '2016-12-26' 
and (open_price - last_close_price) / last_close_price * 100 <= -7.0


select * from tbl_day
where pub_date = '2016-12-26' 
and (close_price - last_close_price) / last_close_price * 100 >= 9.8 
and (low_price - last_close_price) / last_close_price * 100 <= -9.8 
and (open_price - last_close_price) / last_close_price * 100 <= -7.0 


-- 
select * from tbl_day
where pub_date like '2016%'
and (close_price - last_close_price) / last_close_price * 100 >= 9.8 
and (open_price - last_close_price) / last_close_price * 100 <= -7.0 
and (low_price - last_close_price) / last_close_price * 100 <= -9.8 


-- 
select * from tbl_day
where pub_date=pub_date
and (close_price - last_close_price) / last_close_price * 100 >= 9.8 
and (open_price - last_close_price) / last_close_price * 100 <= -5.0 
and (low_price - last_close_price) / last_close_price * 100 <= -9.8 





