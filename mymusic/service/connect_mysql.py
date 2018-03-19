import pymysql


class MyConn:
    __ip = "localhost"
    __userName = "root"
    __password = "123456"
    __dbName = "mymusic"

    def __init__(self):
        pass

    # 获取连接对象
    def get_db(self):
        return pymysql.connect(self.__ip, self.__userName, self.__password, self.__dbName, charset='utf8')

    # 获取游标对象
    def get_cursor(self):
        db = self.get_db()
        return db.cursor()

    # 执行sql
    def execute_no_trans(self, sql, args):
        cursor = self.get_cursor()
        cursor.execute(sql, args)
        return cursor

    # 查询单条记录
    def select_one(self, sql, args):
        db = self.get_db()
        try:
            cursor = db.cursor()
            cursor.execute(sql, args)
            return cursor.fetchone()
        except BaseException:
            pass
        finally:
            db.close()

    # 查询所有记录
    def select_all(self, sql, args):
        db = self.get_db()
        try:
            cursor = db.cursor()
            cursor.execute(sql, args)
            return cursor.fetchall()
        except BaseException:
            pass
        finally:
            db.close()

    # 执行sql  带事务
    def execute_trans(self, sql, args):
        db = self.get_db()
        try:
            cursor = db.cursor()
            count = cursor.execute(sql, args)
            db.commit()
            return count
        except BaseException as err:
            print(err.__str__())
            db.rollback()
        finally:
            db.close()
