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
        sql = f"select * from ysoft_gif limit {page_no}, {(page_no+1) * 10}"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @db
    def switchs(cursor):
        sql = "select * from ysoft_switch where id=1"
        cursor.execute(sql)
        return cursor.fetchone()

