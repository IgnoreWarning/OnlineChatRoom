import socket as sk
import time as t
import json


class Client(object):
    """ 客户端类，封装了客户端的一些常用功能以供外部调用

    属性：
        IP(str):客户端程序使用的IP地址
        PORT(str):客户端程序使用的端口号
        connectSocket(socket对象):连接套接字，用于与服务端建立连接
        nickname(str):当前客户端对应的用户的昵称，用于登陆验证以及聊天消息的处理
        isClosed(bool):用于标识客户端与服务端的连接是否关闭

    """

# 构造方法
    def __init__(self):
        """构造函数，用于初始化client对象"""
        self.__IP = '127.0.0.1'
        self.__PORT = 50000
        self.__connectSocket = None
        self.__nickname = None
        self.__isClosed = False

# 建立连接
    def getConnection(self):
        """连接函数，用于与服务端建立连接，返回值为空"""
        self.__connectSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        address = (self.__IP, self.__PORT)
        self.__connectSocket.connect(address)
        return None

# 设置昵称
    def setNickname(self, nickname: str):
        """用于设置当前客户端对应的用户的昵称

        参数:
            self:表明该函数是一个实例方法
            nickname(str):通过外部获得的客户端的昵称

        返回值:None
        """
        self.__nickname = nickname
        return None

# 登录验证
    def loginCheck(self, loginInfo: str) -> int:
        """登录验证函数，用于客户端在登录时进行身份的验证

        参数:
            self:表明该函数是一个实例方法
            loginInfo(str):用户输入登录信息，由用户名和密码组成的字符串

        返回值:
            status(int):不同的值代表了不同的登录结果
        """
        messageDict = {'source': self.__nickname, 'destination': None, 'type': 'login', 'data': loginInfo}
        messageJSON = json.dumps(messageDict)
        self.__connectSocket.send(messageJSON.encode())
        t.sleep(0.3)
        status = int(self.__connectSocket.recv(10).decode())
        return status

# 消息处理
    def processMessage(self, targetUser: str, messageType: str, message: str) -> str:
        """消息处理函数，用于发送消息前对消息进行一定的处理

        参数:
            self:表明该函数是一个实例方法
            targetUser(str):消息发送目标客户端的用户的昵称
            messageType(str):消息的类别
            message(str):消息的具体内容

        返回值:
            messageJSON(str):经过处理后以json格式封装的消息数据
        """
        messageDict = {'source': self.__nickname, 'destination': targetUser, 'type': messageType, 'data': message}
        messageJSON = json.dumps(messageDict)
        return messageJSON

# 发送消息
    def sendMessage(self, message: str):
        """消息发送函数，用于将封装好的消息发送给服务端

        参数:
            self:表明该函数是一个实例方法
            message(str):将要被发送的消息数据

        返回值:None
        """
        self.__connectSocket.send(message.encode())
        return None

# 接收消息
    def receiveMessage(self) -> str:
        """消息接收函数，用于接收服务端转发来的消息信息

        参数:
            self:表明该函数是一个实例方法

        返回值:
            message(str):经过解码后的消息数据

        """
        message = None
        try:
            message = self.__connectSocket.recv(1024).decode()
        except ConnectionResetError:
            print("与服务端的连接已被关闭")
        return message

# 关闭连接
    def closeConnection(self):
        """关闭连接函数，用于客户端与服务端之间结束通信

        参数:
            self:表明该函数是一个实例方法

        返回值:None
        """
        messageDict = {'source': self.__nickname, 'destination': None, 'type': 'exit', 'data': None}
        messageJSON = json.dumps(messageDict)
        self.__connectSocket.send(messageJSON.encode())
        t.sleep(1)
        self.__connectSocket.close()
        self.__isClosed = True
        return None

# 返回当前连接状态
    def isClosed(self) -> bool:
        """返回客户端当前与服务端的连接是否关闭

        参数:
            self:表明该函数是一个实例方法

        返回值:
            bool:True 表明连接已关闭；False 表明连接未关闭
        """
        return self.__isClosed
