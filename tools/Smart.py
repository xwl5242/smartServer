# -*- coding:utf-8 -*-
import time
from config.DB import db


class Smart:

    @staticmethod
    @db
    def suggest_save(cursor, suggest):
        if suggest:
            sql = f"insert into ysoft_suggest(suggest,create_time,del_flag) " \
                f"values('{suggest}',{time.time()},'0')"
            cursor.execute(sql)

    @staticmethod
    @db
    def gif_save(cursor, gif_id, title, img):
        sql = f"insert ignore into ysoft_gif(id,title,img) values('{gif_id}','{title}','{img}')"
        cursor.execute(sql)

    @staticmethod
    @db
    def gif_query(cursor, page_no):
        sql = f"select * from ysoft_gif limit {page_no * 10}, {10}"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @db
    def switchs(cursor):
        sql = "select * from ysoft_switch where id=1"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db
    def switch_ver(cursor, ver):
        sql = f"select * from ysoft_switch where ver='{ver}'"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db
    def ub_select(cursor, uuid):
        sql = f"select * from u_browser where id='{uuid}' and del_flag='0'"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db
    def ub_save(cursor, uuid):
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = f"insert ignore into u_browser(id,create_time) values('{uuid}', '{create_time}')"
        return cursor.execute(sql)

    @staticmethod
    @db
    def ub_update(cursor, uuid, col_name, col_value):
        sql = f"update u_browser set {col_name}='{col_value}' where id='{uuid}' and del_flag='0'"
        return cursor.execute(sql)

