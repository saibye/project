
-- user
insert into t_trc_user (user_id, user_name, user_mail, enable) values ('wang',  'allen', 'allen@163.com', '1');
insert into t_trc_user (user_id, user_name, user_mail, enable) values ('debug', 'tom', 'tom@163.com', '1');


-- reg
insert into t_trc_reg (user_id, stock_id) values ('wang', '000725');
insert into t_trc_reg (user_id, stock_id) values ('wang', '300279');
insert into t_trc_reg (user_id, stock_id) values ('wang', '300750');
insert into t_trc_reg (user_id, stock_id) values ('wang', '601066');
insert into t_trc_reg (user_id, stock_id) values ('wang', '002594');

insert into t_trc_reg (user_id, stock_id) values ('debug', '000725');
insert into t_trc_reg (user_id, stock_id) values ('debug', '300750');
insert into t_trc_reg (user_id, stock_id) values ('debug', '601066');
insert into t_trc_reg (user_id, stock_id) values ('debug', '002594');


-- ma
insert into t_trc_ma  (user_id, ma) values ('wang', 20);
insert into t_trc_ma  (user_id, ma) values ('wang', 50);
insert into t_trc_ma  (user_id, ma) values ('wang', 200);

insert into t_trc_ma  (user_id, ma) values ('debug', 20);
insert into t_trc_ma  (user_id, ma) values ('debug', 50);

#
