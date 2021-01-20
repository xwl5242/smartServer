# -*- coding:utf-8 -*-
import time
from config.DB import db


class Smart:

    @staticmethod
    @db
    def suggest_save(cursor, suggest):
        sql = f"insert into ysoft_suggest(suggest,create_time,del_flag) " \
            f"values('{suggest}',{time.time()},'0')"
        cursor.execute(sql)


