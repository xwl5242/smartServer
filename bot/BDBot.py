# -*- coding:utf-8 -*-
import uuid
import time
import json
import random
import requests
from config.DB import db
from config.Config import Conf


class BDUnitBot:
    BD_ACCESS_TOKEN_KEY = 'bd_access_token'
    """
    百度UNIT，闲聊机器人
    """
    @staticmethod
    def __oauth():
        """
        请求获取access_token
        :return:
        """
        # header
        header = {"Content-Type": "application/json;charset=UTF-8", "Connection": "close"}
        # 请求参数
        data = {
            "grant_type": "client_credentials",
            "client_id": Conf.BOT_API_KEY,
            "client_secret": Conf.BOT_API_SECRET
        }
        # 请求
        r = requests.post(url=Conf.BOT_OAUTH_URL, headers=header, data=data)
        r = json.loads(r.text)
        # 获取access_token
        access_token = r.get('access_token')
        expires_in = r.get('expires_in')
        last_time = int(time.time())
        # 存入redis
        BDUnitBot.set_access_token(access_token, last_time, expires_in)
        return access_token

    @staticmethod
    def access_token():
        """
        获取access_token
        :return:
        """
        c_access_token = BDUnitBot.get_access_token()
        if c_access_token:
            if int(time.time()) - (int(c_access_token['last_time'])+int(c_access_token['expires_in'])/30) < 0:
                return c_access_token['access_token']
            else:
                return BDUnitBot.__oauth()
        else:
            return BDUnitBot.__oauth()

    @staticmethod
    def chat(uid, content):
        """
        闲聊
        :param uid: 用户唯一id(wxid)
        :param content: 用户的消息
        :return:
        """
        # 先查询用户对话是否失效，默认三分钟无对话即为失效
        session_ = BDUnitBot.get_chat_session(uid)
        if session_:
            lct = int(session_['last_chat_time'])
            if (int(time.time()) - lct) > 3*60:
                session_id = ''
            else:
                session_id = session_['session_id']
        else:
            session_id = ''
        # 调用百度UNIT的access_token
        access_token = BDUnitBot.access_token()
        # 闲聊
        return BDUnitBot.__chat(uid, session_id, content, access_token)

    @staticmethod
    def __chat(uid, session_id, content, access_token):
        """
        聊天
        :param uid: 用户唯一id
        :param session_id: 对话session_id
        :param content: 对话内容
        :param access_token: 请求access_token
        :return:
        """
        url = Conf.BOT_URL + '?access_token=' + access_token
        data = {
            "log_id": str(uuid.uuid4()),
            "version": "2.0",
            "service_id": Conf.BOT_SERVICE_ID,
            "session_id": session_id,
            "request": {
                "query": content,
                "user_id": uid
            }
        }
        r = requests.post(url=url, headers={"Content-Type": "application/json"}, data=json.dumps(data).encode("utf-8"))
        resp = json.loads(r.text)
        if resp:
            if resp['error_code'] == 0:
                # 闲聊回复成功
                resp = resp['result']
                resp_list = list(resp['response_list'])
                if resp_list and len(resp_list) > 0:
                    action_list = list(resp_list[0]['action_list'])
                    if action_list and len(action_list) > 0:
                        BDUnitBot.set_chat_session(uid, resp['session_id'], int(time.time()))
                        reply_ = random.choice(action_list).get('say')
                        return uid, reply_
        return uid, None

    @staticmethod
    @db
    def set_access_token(cursor, access_token, last_time, expires_in, del_flag='0'):
        sql = f"insert into bd_bot_access_token(access_token,last_time,expires_in,del_flag) " \
            f"values('{access_token}',{last_time},{int(expires_in)},'{del_flag}')"
        cursor.execute(sql)

    @staticmethod
    @db
    def get_access_token(cursor):
        sql = f"select * from bd_bot_access_token where del_flag='0'"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @db
    def set_chat_session(cursor, u_id, session_id, last_chat_time, del_flag='0'):
        insert_sql = f"insert into bd_bot_chat_session(u_id,session_id,last_chat_time,del_flag) " \
            f"values('{u_id}','{session_id}',{int(last_chat_time)},'{del_flag}')"
        update_sql = f"update bd_bot_chat_session set session_id='{session_id}',last_chat_time={int(last_chat_time)} " \
            f"where u_id='{u_id}'"
        session = BDUnitBot.get_chat_session(u_id)
        if session and session['session_id']:
            cursor.execute(update_sql)
        else:
            cursor.execute(insert_sql)

    @staticmethod
    @db
    def get_chat_session(cursor, u_id):
        sql = f"select * from bd_bot_chat_session where u_id='{u_id}'"
        cursor.execute(sql)
        return cursor.fetchone()
