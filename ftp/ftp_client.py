from socket import *
import sys,os,time

#具体功能
class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  #等待请求
        #等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            data = self.sockfd.recv(4096).decode()
            files = data.split(",")
            for file in files:
                print(file)
        else:
            print("无法完成",data)
    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self,filename):
        self.sockfd.send(("G "+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data =="OK":
            fd = open(filename,"wb")
            while True:
                data = self.sockfd.recv(1024)
                if data ==b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)
    def do_put(self,filename):
        # self.sockfd.send(("P "+filename).encode())
        # data = self.sockfd.recv(128).decode()
        # if data =="OK":
        #     try:
        #         fd = open(filename,"rb")
        #     except IOError:
        #         print("文件不存在")
        #         return
        #     while True:
        #         data = fd.read(1024)
        #         if not data:
        #             time.sleep(0.1)
        #             self.sockfd.send(b"##")
        #             break
        #         self.sockfd.send(data)
        #     print("上传文件完成")
        #     fd.close()

        #老师编写
        try:
            fd = open(filename,"rb")
        except IOError:
            print("文件不存在")
            return
        #获取真实文件名，可能输入路径，对路径的解析
        filename = filename.split("/")[-1]
        self.sockfd.send(("P "+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data =="OK":
            while True:
                data = fd.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            print("上传文件完成")
            fd.close()
        else:
            print(data)

                




def main():  #网络连接
    ADDR = ("127.0.0.1",5555)
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print("连接异常",e)
        return
    ftp = FtpClient(s)
    while True:
        print("**********命令选项*********")
        print("*           list          *")
        print("*         get    file     *")
        print("*         put    file     *")
        print("*            quit         *")
        print("***************************")
        cmd = input("输入命令>>")
        if cmd.strip()=="list":
            ftp.do_list()
        elif cmd[:3]=="get":
            filename = cmd.split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3]=="put":
            filename = cmd.split(" ")[-1]
            ftp.do_put(filename)
        elif cmd.strip()=="quit":
            ftp.do_quit()
        
        else:
            print("请输入正确指令:")

if __name__=="__main__":
    main()