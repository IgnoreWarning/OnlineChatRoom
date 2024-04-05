import tkinter as tk
import threading as td
import time as t
from tkinter import messagebox
from datetime import datetime
from typing import List, Tuple, Union
from Client import *


class ChatWindow(tk.Tk):
    """客户端聊天界面类，封装了一些创建界面需要用到的方法

    属性:
        width(int):登录界面的宽度
        height(int):登陆界面的高度
        messageDisplayType(str):消息显示样式，不同的消息类别对应不同的样式
        onlineUserInfo(str):在线用户信息，用于存储服务端发来的在线用户信息
        client(Client):客户端类的实例对象，用于调用客户端类的相关函数
    """

# 构造函数
    def __init__(self, client: 'Client'=None, master=None):
        """构造函数，用于聊天界面的初始化"""
        super().__init__(master)
        self.width = 800
        self.height = 600
        self.messageDisplayType = "selfMessage"
        self.onlineUserInfo = None
        self.client = client

# 设置窗口居中
    def setCenterWindow(self):
        """设置窗口居中函数，用于获取屏幕的居中位置

         参数:
             self:表明该函数是一个实例方法

         返回值:
             position(str):存储了屏幕居中位置信息的字符串
         """
    # 得到屏幕宽度，高度
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
    # 计算居中时的宽和高
        centerWidth = (screenWidth - self.width) / 2
        centerHeight = (screenHeight - self.height) / 2
    # 返回信息
        position = "%dx%d+%d+%d" % (self.width, self.height, centerWidth, centerHeight)
        return position

# 创建菜单栏函数
    def createMenu(self):
        """用于在聊天窗口创建菜单栏"""
        self.menubar = tk.Menu(self)
        self.fileMenu = tk.Menu(self.menubar, tearoff=0)  # 设置文件分菜单
        self.menubar.add_cascade(label="文件(F)", menu=self.fileMenu)
    # 在文件菜单中建立菜单列表
        self.fileMenu.add_command(label="更新用户列表(R)", command=self.__displayOnlineUser)
        self.fileMenu.add_separator()  # 设置分隔线
        self.fileMenu.add_command(label="清空聊天记录(C)", command=self.__cleanChatMessage)
        self.fileMenu.add_separator()  # 设置分隔线
        self.fileMenu.add_command(label="退出(Q)", command=self.__exitWindow)
    # 显示菜单栏
        self.config(menu=self.menubar)
    # 绑定快捷键
        self.fileMenu.bind_all("<Control-r>", self.__displayOnlineUser)
        self.fileMenu.bind_all("<Control-c>", self.__cleanChatMessage)
        self.fileMenu.bind_all("<Control-q>", self.__exitWindow)
        return None

# 设置窗口布局
    def setWindowPlace(self):
        """窗口布局函数，用于设置窗口组件的布局"""

    # 设置窗口管理组件
    # 显示边界条 showhandle=True, sashrelief=tk.SUNKEN
        self.outerPanedWindow = tk.PanedWindow(orient=tk.HORIZONTAL)
        self.leftInnerPanedWindow = tk.PanedWindow(orient=tk.VERTICAL)
        self.rightInnerPanedWindow = tk.PanedWindow(orient=tk.VERTICAL)
# 用户列表滚动条
        self.listScrollBar = tk.Scrollbar(self.leftInnerPanedWindow, width=10)
        self.listScrollBar.pack(side=tk.RIGHT, fill=tk.Y)
# 在线用户列表
        self.onlineUserList = tk.Listbox(self.leftInnerPanedWindow, borderwidth=2,
                                         relief="groove", font=("微软雅黑", 10), highlightthickness=0,
                                         selectmode=tk.SINGLE, yscrollcommand=self.listScrollBar.set)
    # 设置滚动条
        self.listScrollBar.config(command=self.onlineUserList.yview)
    # 聊天框滚动条
        self.chatScrollBar = tk.Scrollbar(self.rightInnerPanedWindow)
        self.chatScrollBar.pack(side=tk.RIGHT, fill=tk.Y)
# 聊天框
        self.chatBox = tk.Text(self.rightInnerPanedWindow, borderwidth=2,
                               relief="groove", font=("微软雅黑", 13, "bold"), state=tk.DISABLED,
                               background="ghostwhite", yscrollcommand=self.chatScrollBar.set)
    # 设置滚动条
        self.chatScrollBar.config(command=self.chatBox.yview)
# 输入框
        self.inputText = tk.Text(self.rightInnerPanedWindow, borderwidth=2, relief="groove", font=("微软雅黑", 12))
    # 聊天框字体显示样式
        self.chatBox.tag_configure("timeStyle", justify="center", foreground="blueviolet")
        self.chatBox.tag_configure("selfMessage", foreground="royalblue")
        self.chatBox.tag_configure("publicMessage", foreground="seagreen")
        self.chatBox.tag_configure("privateMessage", foreground="firebrick")

# 按钮
        self.buttonSend = tk.Button(self.rightInnerPanedWindow, text="发送", command=None, width=8,
                                    borderwidth=2, relief="ridge", font=("微软雅黑", 12))
        self.buttonClean = tk.Button(self.rightInnerPanedWindow, text="清空", command=None, width=8,
                                     borderwidth=2, relief="ridge", font=("微软雅黑", 12))
# 按钮绑定回调函数
        self.buttonSend.bind("<ButtonRelease-1>", self.__sendInputText)
        self.buttonClean.bind("<ButtonRelease-1>", self.__cleanInputText)

# 列表框绑定回调函数
        self.onlineUserList.bind("<ButtonRelease-1>", self.__getTargetUser)
        self.onlineUserList.bind('<ButtonRelease-3>', lambda e: self.onlineUserList.selection_clear(0, tk.END))

# 添加子组件
        self.outerPanedWindow.add(self.leftInnerPanedWindow, width=160)
        self.outerPanedWindow.add(self.rightInnerPanedWindow)
        self.leftInnerPanedWindow.add(self.onlineUserList)
        self.rightInnerPanedWindow.add(self.chatBox)
        self.rightInnerPanedWindow.add(self.inputText)
        self.rightInnerPanedWindow.add(self.buttonSend)
        self.rightInnerPanedWindow.add(self.buttonClean)
        self.outerPanedWindow.pack(fill=tk.BOTH, expand=True)

# 绝对布局
        self.onlineUserList.place(width=140, height=570, x=5, y=10)
        self.chatBox.place(width=600, height=400, x=10, y=10)
        self.inputText.place(width=500, height=150, x=10, y=430)
        self.buttonSend.place(height=60, x=520, y=430)
        self.buttonClean.place(height=60, x=520, y=520)

        return None


# 创建聊天窗口
    def createChatWindow(self):
        """聊天窗口创建函数，用于创建聊天窗口"""
        self.title("聊天")
        self.geometry(self.setCenterWindow())
        self.createMenu()
        self.setWindowPlace()
    # 设置用户直接退出窗口时调用的函数
        self.protocol("WM_DELETE_WINDOW", self.__closeWindow)
        return None

# 获取系统时间
    def __getSystemTime(self) -> str:
        """用于获取系统当前时间

        参数:
            self:表明该函数是一个实例方法

        返回值:
            timeInfo(str):格式化之后当前系统时间的字符串
        """
        nowTime = datetime.now()
    # 时间格式化
        timeInfo = nowTime.strftime("%Y年%m月%d日 %H:%M:%S")
        return timeInfo

# 列表框显示在线用户
    def __displayOnlineUser(self, event=None):
        """用于在列表框中显示在线用户昵称"""
        onlineUserList = self.__getOnlineUser()
    # 清空在线列表
        self.onlineUserList.delete(0, tk.END)
        for name in onlineUserList:
            if len(name) == 0:
                break
            self.onlineUserList.insert(tk.END, ("{}".format(name)))
        return None

# 获取在线用户
    def __getOnlineUser(self) -> List[str]:
        """用于向服务端发送请求，获取当前在线用户信息

        参数:
            self:表明该函数是一个实例方法

        返回值:
            userList:值为当前在线用户昵称的字符串列表
        """
        messageDestination = "source"
        messageType = "get"
        message = None
        messsageData = self.__messageProcess(messageDestination, messageType, message)
        self.client.sendMessage(messsageData)
        if self.onlineUserInfo == None:
            userList = []
        else:
            userList = list(self.onlineUserInfo.split(" "))
        return userList


# 获取单个在线用户信息,用于向特定用户转发消息
    def __getTargetUser(self, event=None) -> Union[str, None]:
        """回调函数，当用户在在线用户列表中选择用户时调用此函数

        参数:
            self:表明该函数是一个实例方法
            event:表明这是事件触发函数

        返回值:
            name(str):当前用户所选中的在线用户的用户名，None表示用户没有选中任何在线用户
        """
        index = self.onlineUserList.curselection()
        if len(index) == 0:
            name = None
        else:
            name = self.onlineUserList.get(index)
        return name

#  获取消息类别，用于服务端处理
    def __getMessageType(self) -> Tuple[str, str]:
        """用于获取消息的类别，以便聊天数据的封包处理

        参数:
            self:表明该函数是一个实例方法

        返回值:
            tuple:一个由消息的目标用户的用户名和消息类别组成的二元组
        """
        destination = self.__getTargetUser()
        if destination == None:
            messageType = "public"
        else:
            messageType = "private"
        return (destination, messageType)

# 消息处理函数
    def __messageProcess(self, targetUser: str, messageType: str, message: str) -> str:
        """消息处理函数，用于在发送消息前对消息进行一定的处理

        参数:
            self:表明该函数是一个实例方法
            targetUser(str):消息的目标用户
            messageType(str):消息的具体类别
            message(str):消息的具体内容

        返回值:
            data(str):经过处理后的消息字符串
        """
        data = self.client.processMessage(targetUser, messageType, message)
        return data


# 输入框确认发送
    def __sendInputText(self, event=None):
        """回调函数，当用户确认发送输入框中的消息时调用此函数"""
        message = self.inputText.get("1.0", "end-1c")
        destination, messageType = self.__getMessageType()
        if (len(message) == 0 or message.isspace() == True):
            messagebox.showinfo(title="提示", message="输入不能为空")
        else:
            self.messageDisplayType = "selfMessage"
            self.__showChatMessage(message)
            messageData = self.__messageProcess(destination, messageType, message)
            self.client.sendMessage(messageData)
            self.inputText.delete("1.0", "end")
        return None

# 接收聊天消息
    def __receiveChatMessage(self):
        """用于接收服务端转发的来自其它客户端的消息信息并将消息显示在聊天框"""
        while True:
            if self.client.isClosed() == True:
                break

            messageJSON = self.client.receiveMessage()

            try:
                messageDict = json.loads(messageJSON)
            except json.JSONDecodeError:
                continue

            messageSource = messageDict["source"]
            messageDestination = messageDict["destination"]
            messageType = messageDict["type"]
            message = messageDict["data"]

            if messageType == "public":
                self.messageDisplayType = "publicMessage"
            elif messageType == "private":
                self.messageDisplayType = "privateMessage"
            elif messageType == "get":
                self.onlineUserInfo = message
                continue
            else:
                continue

            self.__showChatMessage(nickname=messageSource, message=message)

        return None

# 输入框清空发送
    def __cleanInputText(self, event=None):
        """回调函数，当用户按下相应的按钮时调用此函数清空输入框"""
        self.inputText.delete("1.0", "end")
        return None

# 聊天框显示消息
    def __showChatMessage(self, message: str, nickname: str = "我"):
        """用于在聊天框显示发送和接收到的聊天消息

        参数:
            self:表明该函数是一个实例方法
            message(str):消息的具体内容
            nickname(str):消息的发送者的昵称

        返回值:None
        """
        self.chatBox.configure(state="normal")
        currentTime = self.__getSystemTime() + '\n'
        messageInfo = "{}：{}\n\n".format(nickname, message)
        self.chatBox.insert(tk.END, currentTime, "timeStyle")
        self.chatBox.insert(tk.INSERT, messageInfo, self.messageDisplayType)
        self.chatBox.see(tk.END)
        self.chatBox.configure(state="disabled")
        return None

# 清空聊天框消息
    def __cleanChatMessage(self, event=None):
        """回调函数，当用户按下相应的按钮时调用此函数清空聊天框"""
        self.chatBox.configure(state=tk.NORMAL)
        self.chatBox.delete("1.0", "end")
        self.chatBox.configure(state=tk.DISABLED)
        return None

# 直接关闭窗口
    def __closeWindow(self):
        """回调函数，当用户直接关闭聊天窗口时调用此函数"""
        self.destroy()
        self.client.closeConnection()
        return None

# 退出窗口
    def __exitWindow(self, event=None):
        """回调函数，当用户从菜单栏退出聊天窗口时调用此函数"""
    # 弹出对话框
        result = messagebox.askokcancel(title="提示", message="退出将关闭当前连接，确定要退出吗？")
        if result == True:
            self.destroy()
            self.client.closeConnection()
        return None

# 主函数
    def main(self) -> int:
        """用于创建聊天窗口并开启客户端的多线程消息接收函数

        参数:
            self:表明该函数是一个实例方法

        返回值:
            int:返回数字0表明程序正常执行结束
        """
        self.createChatWindow()

        try:
            thread = td.Thread(target=self.__receiveChatMessage)
            thread.setDaemon(True)
            thread.start()
        except Exception:
            print("线程已关闭")

        return 0

