import configparser
import os
 
conf= configparser.ConfigParser()

def readConf():
    conf.read('app.conf')
    print(conf)
    name = conf.get("mysql", "host")  # 获取指定section 的option值
    print(name)

readConf()

