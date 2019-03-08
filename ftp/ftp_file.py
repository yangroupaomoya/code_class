'''
ftp 文件服务器
ftp_file.py训练
'''
from socket import *
import os,sys
import signal
import time
#全局变量
HOST = "0.0.0.0"
PORT = 5555
ADDR = (HOST,PORT)
FILE_PATH = "/home/tarena/test/net/day7/"

class FtpServer(object):
    def __init__(self,conn):
        self.conn = conn

    def do_list(self):
        file_list = os.listdir(FILE_PATH)
        if not file_list:
            self.conn.send("文件库为空".encode())
        else:
            self.conn.send(b"OK")
            time.sleep(0.1)  #防止粘包
        files = ""
        for file in file_list:
            if file[0] != "." and os.path.isfile(FILE_PATH+file):
                files = files+file+","
            #将拼接好的字符串传给客户端
        self.conn.send(files.encode())

    def do_get(self,filename):
        try:
            fd = open(FILE_PATH+filename,"rb")
        except IOError:
            self.conn.send("文件不存在".encode())
            return
        else:
            self.conn.send(b"OK")
            time.sleep(0.1)
        #发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.conn.send(b"##")
                break
            self.conn.send(data)
        fd.close()
    def do_put(self,filename):
        # file_list = os.listdir(FILE_PATH)
        # if filename in file_list:
        #     self.conn.send("文件已存在".encode())
        #     return
        #老师编写
        if os.path.exists(FILE_PATH+filename):
            self.conn.send("文件已存在".encode())
            return
          
        
        else:
            self.conn.send(b"OK")
            fd = open(FILE_PATH+filename,'wb')
            while True:
                data = self.conn.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            
            fd.close()
                
                
                
            

 

def do_request(conn):
    ftp = FtpServer(conn)
    while True:
        data = conn.recv(1024).decode()
        if data[0]=="Q" or not data:
            conn.close()
            return
        elif data[0]=="L":
            ftp.do_list()
        elif data[0]=="G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0]=="P":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)

        



#网络搭建
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,2)
    s.bind(ADDR)
    s.listen(5)
    #处理僵尸进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print("Listen to the port 6666")

    while True:
        try:
            conn,addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("服务器退出")
        except Exception as e:
            print("Error:",e)
            continue
        print("连接客户端",addr)
        pid = os.fork()  #创建子进程
        if pid == 0:
            s.close()
            do_request(conn)
            os._exit(0)

        else:
            conn.close()


        


if __name__ == "__main__":
    main()