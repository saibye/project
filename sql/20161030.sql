--

-- 
desc tbl_day


--
select close_price , open_price, deal_total_count, deal_total_amount
from tbl_day
where stock_id = '000420'
and pub_date   = '2016-08-26'


select close_price , open_price, deal_total_count, deal_total_amount
from tbl_day
where stock_id = '000420'
and pub_date  like '2016-10%'


select count(1) from tbl_day;


select pub_date, close_price, last_close_price, deal_total_count, deal_total_amount
from tbl_day
where stock_id='000001'


truncate table tbl_day

select stock_id, count(1) from tbl_day
group by stock_id
order by 1;




-- sql
