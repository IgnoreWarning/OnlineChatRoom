import tkinter as tk
import time as t
from tkinter import messagebox
from tkinter import ttk
from Client import *


class LoginWindow(tk.Tk):
    """客户端登录界面类，封装了一些创建界面需要用到的方法

    属性:
        width(int):登录界面的宽度
        height(int):登陆界面的高度
        client(Client):客户端类的实例对象，用于调用客户端类的相关函数
    """

# 构造函数
    def __init__(self, client: 'Client' = None, master=None):
        """构造函数，用于登录界面的初始化"""
        super().__init__(master)
        self.width = 450
        self.height = 300
        self.client = client
        self.createLoginWindow()

# 设置窗口居中
    def setCenterWindow(self) -> str:
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

# 设置窗口布局
    def setWindowPlace(self):
        """窗口布局函数，用于设置窗口组件的布局

        参数:
            self:表明该函数是一个实例方法

        返回值:None
        """
    # 输入框
        self.nicknameLable = tk.Label(self, text="用户名:", width=8, font=("微软雅黑", 12))
        self.nicknameEntry = tk.Entry(self, width=25, font=("微软雅黑", 12), borderwidth=2, relief="ridge")
        self.passwordLable = tk.Label(self, text="密码:", width=8, font=("微软雅黑", 12))
        self.passwordEntry = tk.Entry(self, width=25, show='*', font=("微软雅黑", 12), borderwidth=2, relief="ridge")
    # 进度条
        self.progressBarFrame = tk.Frame(self, width=450, height=10)
        self.progressBar = ttk.Progressbar(self.progressBarFrame, length=450, maximum=1,
                                           value=0, mode='determinate', orient=tk.HORIZONTAL)

    # 按钮
        self.buttonConfirm = tk.Button(self, text="确定", command=None, width=8,
                                       font=("微软雅黑", 12), borderwidth=2, relief="ridge")
        self.buttonCancle = tk.Button(self, text="取消", command=None, width=8,
                                      font=("微软雅黑", 12), borderwidth=2, relief="ridge")
        self.buttonConfirm.bind("<ButtonRelease-1>", self.confirmCreate)
        self.buttonCancle.bind("<ButtonRelease-1>", self.__closeWindow)

    # 布局
        self.nicknameLable.place(x=50, y=80)
        self.nicknameEntry.place(x=150, y=80)

        self.passwordLable.place(x=50, y=140)
        self.passwordEntry.place(x=150, y=140)

        self.buttonConfirm.place(x=70, y=220)
        self.buttonCancle.place(x=290, y=220)

        self.progressBar.grid(row=0, column=0, sticky="wens")

    # 设置父组件的大小不由子组件决定
        self.progressBarFrame.grid_propagate(False)
        self.progressBarFrame.rowconfigure(0, weight=1)
        self.progressBarFrame.columnconfigure(0, weight=1)

        return None

# 创建登录窗口
    def createLoginWindow(self):
        """登录窗口创建函数，用于创建登录窗口"""
        self.title("登录")
        self.geometry(self.setCenterWindow())
        self.setWindowPlace()
    # 设置用户直接退出窗口时调用的函数
        self.protocol("WM_DELETE_WINDOW", self.__closeWindow)
        return None

# 输出提示信息
    def __showPromptInfo(self, status: int):
        """提示信息输出函数，用于输出提示信息

         参数:
            self:表明该函数是一个实例方法
            status(int):登录状态标志，不同的数字代表了不同的登录状态

        返回值:None
        """
        if status == 0:
            promptInfo = "注册成功"
        elif status == 2:
            promptInfo = "登录成功"
        else:
            promptInfo = "密码错误"

        if (status == 0 or status == 2):
            messagebox.showinfo("提示", promptInfo)
            self.destroy()
        else:
            messagebox.showerror("提示", promptInfo)

        return None

# 进度条显示
    def __progressBarDisplay(self):
        """用于在登录界面显示一个进度条，以便用户了解程序的运行状态"""
        self.progressBarFrame.place(x=0, y=280)
        for i in range(0, 12, 1):
            self.progressBar['value'] = i * 0.1
            t.sleep(0.1)
            self.progressBarFrame.update()
        self.progressBarFrame.place_forget()
        return None

# 绑定鼠标事件--确定按钮
    def confirmCreate(self, event=None):
        """回调函数，当用户输入相关信息后点击确认按钮，便会执行该函数

        参数:
            self:表明该函数是一个实例方法
            event:表明这是事件触发函数

        返回值:None
        """
        name = self.nicknameEntry.get()
        password = self.passwordEntry.get()
        loginInfo = name + ' ' + password
        if ((len(name) + len(password) == 0) or (name.isspace() or password.isspace()) == True):
            # 输出提示信息
            messagebox.showinfo("提示", "用户名或密码不能为空")
        else:
            # 发送登录信息
            self.__progressBarDisplay()
            status = self.client.loginCheck(loginInfo)
            self.client.setNickname(nickname=name)
            self.__showPromptInfo(status)
        return None

# 关闭窗口
    def __closeWindow(self, event=None):
        """回调函数，当用户点击取消按钮时调用此函数关闭登录窗口

        参数:
            self:表明该函数是一个实例方法
            event:表明这是事件触发函数

        返回值:None
        """
        self.progressBarFrame.place_forget()
        self.destroy()
        self.client.closeConnection()
        return None
