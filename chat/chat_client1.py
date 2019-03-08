from socket import *
import sys,os
ADDR = ('127.0.0.1',6666)
def send_msg(s,name):  #消息发送
    while True:
        text = input("发言:")
        if "确认退出" in text:
            msg = "确认退出 %s %s"%(name,text)
            s.sendto(msg.encode(),ADDR)
            break

        msg = "C %s %s"%(name,text)
        s.sendto(msg.encode(),ADDR)


def recv_msg(s):  #接收消息
    while True:
        data,addr = s.recvfrom(2048)
        
        print(data.decode())
        if "确认退出" in data.decode():
            
            break

def main():  #创建网络连接创建新的进程
    
    s = socket(AF_INET,SOCK_DGRAM)
    while True:
        name = input('>>请输入姓名:')
        msg = "L "+name
        s.sendto(msg.encode(),ADDR)   #发送请求给服务端
        data,addr = s.recvfrom(1024)
        if data.decode()=="OK":            #等待回应
            print('%s您已进入聊天室'%name)
            break
        else:
            print(data.decode())
    pid = os.fork()#创建新的进程
    if pid < 0:
        sys.exit("Error!")
    elif pid == 0:  #子进程发送消息
        send_msg(s,name)
        
    else:
        recv_msg(s)

if __name__ =="__main__":
    main()