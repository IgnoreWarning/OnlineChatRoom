from LoginWindow import *
from MainWindow import *


# 主函数
def main() -> int:
    """主函数，主要用于对其它模块的调用并执行一些代码逻辑
    返回值:
        int:返回数字0表明程序正常执行结束
    """
# 创建客户端实例
    client = Client()
    client.getConnection()
# 创建登录窗口
    loginWindow = LoginWindow(client=client)
    loginWindow.mainloop()
# 如果用户在登陆界面就退出，则不创建聊天窗口
    if (client.isClosed() == False):
        mainWindow = ChatWindow(client=client)
        mainWindow.main()
        mainWindow.mainloop()

    return 0


# 运行程序
if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("程序异常")
