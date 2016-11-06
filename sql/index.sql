


DROP INDEX idx_k_day on tbl_day;

CREATE INDEX idx_k_day ON tbl_day (stock_id);



--- before
mysql> select max(pub_date) from tbl_day where stock_id='000002';
+---------------+
| max(pub_date) |
+---------------+
| 2016-08-26    |
+---------------+
1 row in set (5.59 sec)


-- after

mysql> select max(pub_date) from tbl_day where stock_id='000002';
+---------------+
| max(pub_date) |
+---------------+
| 2016-08-26    |
+---------------+
1 row in set (0.00 sec)




