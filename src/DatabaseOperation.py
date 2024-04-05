import pymysql as pq
from typing import List, Tuple, Union


class DatabaseUtils(object):
    """数据库工具类，封装了一些对数据库操作需要用到的方法

    属性:
        host(str):数据库服务器的主机名或IP地址，一般为localhost
        port(int):数据库使用的端口，MySQL数据库默认为3306
        user(str):数据库的用户名
        password(str):数据库用户的密码
        database(str):存储数据的数据库名
        table(str):存储数据的数据表名
    """

# 构造函数
    def __init__(self, host="localhost", port=3306, user=None, password=None, database=None, table=None):
        """构造方法，用于对实例对象初始化"""
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database
        self.__table = table

# 与数据库连接
    def __getConnection(self) -> 'Connection':
        """数据库连接函数，用于与数据库进行连接操作

        参数:
            self:表明该函数是一个实例方法

        返回值:
            conn(Connection):Connection类的对象，用于后续对数据库的操作
        """
        conn = pq.connect(host=self.__host, port=self.__port, db=self.__database,
                          user=self.__user, password=self.__password, charset="utf8", autocommit=True)
        return conn

# 关闭连接
    def __closeConnection(self, conn: 'Connection'):
        """关闭连接函数，用于执行操作完成后与数据库断开连接

        参数:
            self:表明该函数是一个实例方法
            conn(Connection):Connection类的对象，用于后续对数据库的操作

        返回值:None
        """
        conn.close()
        return None

# 数据插入
    def insertValues(self, name: str, password: str):
        """数据插入函数，用于将用户的注册信息存入数据库

        参数:
            self:表明该函数是一个实例方法
            name(str):用户输入的用户名
            password(str):用户输入的密码

        返回值:None
        """
        sql = "insert into `%s`.`%s` (`name`, `password`) values ('%s', '%s');" % (
            self.__database, self.__table, name, password)
        conn = self.__getConnection()
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        self.__closeConnection(conn)
        return None

# 数据查询
    def searchValues(self, name: str) -> Union[Tuple[str, str], Tuple[None, None]]:
        """用户数据查询函数，用于查询用户的相关数据

        参数:
            self:表明该函数是一个实例方法
            name(str):用户输入的用户名

        返回值:
            Tuple[str, str]:表示成功查找到用户的数据，返回一个存储用户昵称和密码的二元组
            Tuple[None, None]:表示用户的数据不存在
        """
        sql = "select name, password from `%s`.`%s` where name = '%s';" % (self.__database, self.__table, name)
        conn = self.__getConnection()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        self.__closeConnection(conn)
        if len(data) == 0:
            data = ((None, None),)
        return data[0]


# 数据信息是否存在
    def isExist(self, name: str, password: str) -> int:
        """用于判断用户的相关信息在数据库中是否存在 

        参数:
            self:表明该函数是一个实例方法
            name(str):用户输入的用户名
            password(str):用户输入的密码

        返回值:
            flag(int):用于标识数据的查询结果，flag为0说明账号不存在，flag为1说明账号存在但密码错误，flag为2说明账号密码都正确
        """
        flag = 0
        data = self.searchValues(name)

        if (data[0] == None and data[1] == None):
            flag = 0
            self.insertValues(name=name, password=password)
        else:
            if data[1] == password:
                flag = 2
            else:
                flag = 1

        return flag
