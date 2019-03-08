
    #coding = utf_8
'''
Chatroom
env:python3.5
exc:socket and fork
'''
from socket import *
import os,sys
user = {}   #用于存储用户{name:addr}

def do_login(s,name,addr):  #处理登录
    if name in user:
        s.sendto('该用户已存在'.encode(),addr)
        return
    s.sendto("OK".encode(),addr)
    print("用户申请进入群聊",addr)
    msg = '欢迎%s进入聊天室'%name   #通知其他人
    for i in user:
        s.sendto(msg.encode(),user[i])
    user[name] = addr  #将用户加入user
    print("字典:",user)

    
def do_chat(s,name,text): #处理聊天信息
    msg = "%s : %s"%(name,text)
    for i in user:
        if i != name:
            s.sendto(msg.encode(),user[i])

def do_quit(s,name,addr):  #处理退出
    msg = "您%s已确认退出群聊"%name
    del user[name]
    
    s.sendto(msg.encode(),addr)
    for i in user:
        msg = "%s用户已退出群聊"%name
        s.sendto(msg.encode(),user[i])
    

def do_request(s):  #处理请求
    while True:
        data,addr = s.recvfrom(1024)
        msgList = data.decode().split()
        if msgList[0] == "L":
            do_login(s,msgList[1],addr)
        elif msgList[0]=="C":
            #重新组织消息内容
            text = " ".join(msgList[2:])
            do_chat(s,msgList[1],text)  
        elif msgList[0] == "确认退出":
            do_quit(s,msgList[1],addr)    
            

def main():#创建网络连接
        ADDR = ('0.0.0.0',6666)
        s = socket(AF_INET,SOCK_DGRAM) #创建套接字
        s.setsockopt(SOL_SOCKET,SO_REUSEADDR,2)
        s.bind(ADDR)

        #处理各种客户端请求
        do_request(s)

if __name__ == '__main__':
    main()
    