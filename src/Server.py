import socket as sk
import threading as td
import time as t
import json
import sys
from typing import Tuple, List, Union
import DatabaseOperation as do


class Server(object):
    """服务器类，封装了一些常用的方法供外部调用

    属性:
        IP(str):服务端程序使用的IP地址
        PORT(str):服务端程序使用的端口号
        listenSocket(socket对象):监听套接字，用于监听客户端的连接请求
        idClosed(bool):用于标识服务端是否已经关闭
        connectionDict(Dictionary):用于存储已经与服务端建立连接的客户端的相关信息
    """

# 构造函数
    def __init__(self):
        """构造函数，用于服务端对象初始化"""
        self.__IP = '127.0.0.1'
        self.__PORT = 50000
        self.__listenSocket = None
        self.__isClosed = False
        self.__connectionDict = {}

# 启动服务器
    def startServer(self):
        """服务端启动函数，用于对服务端对象的部分属性进行处理并给出提示信息

        参数:
            self:表明该函数是一个实例方法

        返回值:None
        """
        self.__listenSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.__listenSocket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, True)
        address = (self.__IP, self.__PORT)
        self.__listenSocket.bind(address)
        self.__listenSocket.listen(5)
        self.__listenSocket.settimeout(180)
        print("服务端启动成功，等待客户端连接·······")
        return None

# 连接处理
    def connectionProcess(self) -> Union['socket', str, None]:
        """用于处理客户端的连接请求并返回相应的连接套接字
        参数:
            self:表明该函数是一个实例方法

        返回值:
            socket对象:说明服务端成功接收到了客户端的连接
            str:说明依然有客户端与服务端保持着连接，服务端仍需保持开启状态
            None:说明一段时间内没有收到客户端的连接，如果当前已经没有客户端的连接，则准备关闭服务端
        """
        connectSocket = None
        try:
            connectSocket, addr = self.__listenSocket.accept()
        except KeyboardInterrupt:
            self.closeServer()
            sys.exit("程序已退出")
        except sk.timeout:
            if len(self.__connectionDict) == 0:
                print("长时间无连接，服务器已关闭")
                self.closeServer()
            else:
                self.__listenSocket.settimeout(120)
                connectSocket = 'alive'
        return connectSocket


# 身份验证
    def identityVerification(self, userInfo: str) -> Tuple[str, int]:
        """用于对客户端发来的登录信息进行验证并返回验证结果

        参数:
            self:表明该函数是一个实例方法
            userInfo(str):客户端发来的登录信息，由用户名和密码组成的字符串

        返回值:
            nicknameStatus(tuple):由用户名和验证结果组成的二元组
        """
        dbOperation = do.DatabaseUtils()
        name, password = userInfo.split()
        status = dbOperation.isExist(name=name, password=password)
        nicknameStatus = (name, status)
        return nicknameStatus

# 私聊消息处理
    def relayPrivateMessage(self, sourceUser: str, targetUser: str, message: str):
        """消息私发函数，用于对客户端发来的私聊消息进行转发

        参数:
            self:表明该函数是一个实例方法
            sourceUser(str):消息发送者的昵称
            targetUser(str):消息目标用户的昵称
            message(str):消息的具体内容

        返回值:None
        """
        messageDict = {'source': sourceUser, 'destination': targetUser, 'type': "private", 'data': message}
        messageJSON = json.dumps(messageDict)
        for nickname, connectSocket in self.__connectionDict.items():
            if nickname == targetUser:
                sock = connectSocket
                break
        sock.send(messageJSON.encode())
        return None

# 群聊消息处理
    def relayPublicMessage(self, sourceUser: str, message: str):
        """消息群发函数，用于对客户端发来的群聊消息进行转发

        参数:
            self:表明该函数是一个实例方法
            sourceUser(str):消息发送者的昵称
            message(str):消息的具体内容

        返回值:None
        """
        messageDict = {'source': sourceUser, 'destination': None, 'type': "public", 'data': message}
        messageJSON = json.dumps(messageDict)
        for nickname, connectSocket in self.__connectionDict.items():
            if nickname == sourceUser:
                continue
            else:
                connectSocket.send(messageJSON.encode())
        return None

# 发送在线用户信息
    def sendOnlineUserInfo(self, sourceUser: str):
        """用于发送当前在线用户的信息，当客户端发来获取在线用户信息的请求时，调用此函数

        参数:
            self:表明该函数是一个实例方法
            sourceUser(str):消息发送者的昵称

        返回值:None
        """
        onlineUserList = []
        onlineUserStr = None
        for nickname, connectSocket in self.__connectionDict.items():
            if nickname == sourceUser:
                sock = connectSocket
            else:
                onlineUserList.append(nickname)
        onlineUserStr = " ".join(onlineUserList)
        print(onlineUserStr)
        messageDict = {'source': sourceUser, 'destination': None, 'type': "get", 'data': onlineUserStr}
        messageJSON = json.dumps(messageDict)
        sock.send(messageJSON.encode())
        return None

# 请求处理
    def requestProcess(self, conn: 'socket'):
        """请求处理函数，针对客户端发来的不同请求进行相应的处理

         参数:
            self:表明该函数是一个实例方法
            conn(socket对象):使用连接套接字接收客户端发来的请求

        返回值:None
        """
        while True:
            receiveData = conn.recv(1024).decode()
            print(receiveData)
            messageDict = json.loads(receiveData)

        # 消息解包
            messageType = messageDict['type']
            messageSource = messageDict['source']
            messageDestination = messageDict['destination']
            message = messageDict['data']

        # 根据消息类型进行相应操作
            if messageType == 'login':
                loginInfo = messageDict['data']
                nickname, status = self.identityVerification(loginInfo)
                self.__connectionDict.update({nickname: conn})
                print(self.__connectionDict)
                conn.send(str(status).encode())
            elif messageType == 'get':
                self.sendOnlineUserInfo(messageSource)
            elif messageType == 'public':
                self.relayPublicMessage(messageSource, message)
            elif messageType == 'private':
                self.relayPrivateMessage(messageSource, messageDestination, message)
            elif messageType == "exit":
                self.closeConnection(messageSource)
                break
            else:
                continue

        return None

# 关闭客户端连接
    def closeConnection(self, sourceUser: str):
        """用于关闭服务端与客户端的连接，当客户端发来关闭连接的请求时调用此函数

        参数:
            self:表明该函数是一个实例方法
            sourceUser(str):消息发送者的昵称

        返回值:None
        """
        try:
            conn = self.__connectionDict.pop(sourceUser)
            print("与{}的连接已被关闭".format(sourceUser))
            conn.close()
        except KeyError:
            print("连接已关闭")
        finally:
            print("剩余连接的个数：{}\n{}".format(len(self.__connectionDict), self.__connectionDict))
        return None


# 关闭服务端
    def closeServer(self):
        """当所有的客户端都与服务端的连接断开且在一定时间内没有新的连接建立，则调用此函数关闭服务端

        参数:
            self:表明该函数是一个实例方法

        返回值:None
        """
        self.__isClosed = True
        t.sleep(1)
        self.__listenSocket.close()
        return None


# 获取服务端状态
    def isClosed(self) -> bool:
        """返回服务端当前状态

        参数:
            self:表明该函数是一个实例方法

        返回值:
            bool:True 表明服务端已关闭；False 表明服务端未关闭
        """
        return self.__isClosed


# 主函数
    def main(self) -> int:
        """用于启动服务端并开启服务端的多线程请求处理等服务

        参数:
            self:表明该函数是一个实例方法

        返回值:
            int:返回数字0表明程序正常执行结束
        """
        while True:
            # 查看服务器是否关闭
            if self.isClosed() == True:
                break

            conn = self.connectionProcess()

            if (not isinstance(conn, sk.socket)):
                continue

            thread = td.Thread(target=self.requestProcess, args=(conn, ))
        # 设置守护线程
            thread.daemon = True
            thread.start()

        return 0


# 运行程序
if __name__ == "__main__":
    server = Server()
    server.startServer()
    try:
        server.main()
    except Exception:
        print("程序出现异常")
