# -*- coding:utf-8 -*-
import pymysql
from config.Config import Conf
from dbutils.pooled_db import PooledDB

# database pool
POOL = PooledDB(pymysql, 5, host=Conf.DB_HOST, user=Conf.DB_USER,
                passwd=Conf.DB_PASSWORD, db=Conf.DB_DATABASE, port=Conf.DB_PORT,
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


# database decorator, auto connect and auto close db, cursor
def db(func):
    def wrapper(*args, **kwargs):
        conn = POOL.connection()
        cursor = conn.cursor()
        try:
            return func(cursor, *args, **kwargs)
        except Exception as e:
            import traceback
            print(traceback.print_exc())
            print(repr(e))
            conn.rollback()
        finally:
            conn.commit()
            cursor.close()
            conn.close()
    return wrapper

