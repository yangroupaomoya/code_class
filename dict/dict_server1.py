'''
name: Tedu
modules: pymysql
This is a dict project for AID
'''

from socket import * 
import pymysql
import os 
import sys 
import time
import signal 

#定义一些全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST,PORT)

#网络搭建
def main():
    #创建数据库连接
    db=pymysql.connect('localhost','root','123456',\
    'dict')

    #创建套接子
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    #处理僵尸
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue 
        
        #创建子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c,db) #子进程函数
            sys.exit(0)
        else:
            c.close()

def do_child(c,db):
    while True:
        data = c.recv(128).decode()
        print(c.getpeername(),':',data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit()
        elif data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            do_login(c,db,data)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_hist(c,db,data)

#注册
def do_register(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    
    sql = "select * from user where name='%s'"%name 
    cursor.execute(sql)
    r = cursor.fetchone()

    if r != None:
        c.send(b'EXISTS')
        return 
    
    #插入用户
    sql = "insert into user (name,passwd) values \
    ('%s','%s')"%(name,passwd)

    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except Exception:
        db.rollback()
        c.send(b'FAIL')

def do_login(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql="select * from user where name='%s' and \
    passwd='%s'"%(name,passwd)

    #查找用户
    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        c.send(b'FAIL')
    else:
        c.send(b'OK')   

def do_query(c,db,data):
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()
    #内部函数可以直接使用外部函数变量
    def insert_history():
        tm = time.ctime()
        sql = "insert into hist (name,word,time) \
        values ('%s','%s','%s')"%(name,word,tm)
        #插入历史记录
        try:
            cursor.execute(sql)
            db.commit()
        except Exception:
            db.rollback()

    #使用单词本查找
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'FAIL')
        time.sleep(0.1)
        return 
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:  # tmp大于目标单词
            
            break
        elif tmp == word:
            c.send(line.encode())  
            f.close()
            insert_history()
            return
    c.send(b"FAIL") #到结尾也没有找到
    f.close()
        
def do_hist(c,db,data):
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()
    sql = "select * from hist where name='%s'"%name 
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'FALL')
        return 
    else:
        c.send(b'OK')
        time.sleep(0.1)
    for i in r:
        msg="%s    %s     %s"%(i[1],i[2],i[3])
        c.send(msg.encode())
        time.sleep(0.1)
    c.send(b'##')

if __name__=="__main__":
    main()