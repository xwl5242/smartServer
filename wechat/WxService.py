# -*- coding:utf-8 -*-
import time
from config.DB import db
from config.Config import Conf
from wechatpy.client import WeChatClient
from wechatpy.client.api import WeChatJSAPI, WeChatMedia


ACCESS_TOKEN_TYPE = 'access_token'
JS_API_TICKET_TYPE = 'js_api_ticket'


class WxMediaService(WeChatMedia):
    def __init__(self):
        """
        微信公众号多媒体接口
        """
        client = WeChatClient(Conf.WX_APP_ID, Conf.WX_APP_SECRET,
                              access_token=WxService.fetch_token(ACCESS_TOKEN_TYPE))
        super(WxMediaService, self).__init__(client)


class WxService:

    @staticmethod
    @db
    def save_smart_search(cursor, wx_id, wx_key_word, wx_msg_type, wx_msg_time, wx_msg_id, wx_msg_ret):
        sql = f"insert into wx_msg_smart_reply(wx_id, wx_key_word, wx_msg_type, wx_msg_time, wx_msg_id, wx_msg_ret) " \
            f"values('{wx_id}','{wx_key_word}','{wx_msg_type}',{int(wx_msg_time)},'{wx_msg_id}','{wx_msg_ret}')"
        cursor.execute(sql)

    @staticmethod
    @db
    def query_smart_search(cursor, wx_id, msg_id):
        sql = f"select * from wx_msg_smart_reply where wx_id='{wx_id}' and wx_msg_id='{msg_id}'"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @db
    def fetch_token(cursor, token_type):
        """
        获取wx公众平台access_token和js api ticket
        :param cursor:
        :param token_type: access_token|js_api_ticket
        :return:
        """
        select_sql = f"select token,token_expire from wx_access_token where token_type='{token_type}'"
        cursor.execute(select_sql)
        token = cursor.fetchone()
        if token and token['token'] and token['token_expire']:
            if int(token['token_expire']) < (int(time.time())-5*60*1000):
                expire, token = WxService._fetch_token(token_type)
                if expire and token:
                    sql = f"update wx_access_token set token='{token}',token_expire={expire} " \
                        f"where token_type='{token_type}'"
                    cursor.execute(sql)
                    return token
            else:
                return token['token']
            return None
        else:
            expire, token = WxService._fetch_token(token_type)
            if expire and token:
                sql = f"insert into wx_access_token(token,token_expire,token_type) " \
                    f"values('{token}',{expire},'{token_type}')"
                cursor.execute(sql)
                return token
            return None

    @staticmethod
    def _fetch_token(token_type):
        wx_client = WeChatClient(Conf.WX_APP_ID, Conf.WX_APP_SECRET)
        if token_type == ACCESS_TOKEN_TYPE:
            token = wx_client.access_token
            expire = wx_client.expires_at
            return expire, token
        elif token_type == JS_API_TICKET_TYPE:
            ticket = WeChatJSAPI(wx_client).get_ticket()
            expire = ticket['expires_in']
            token = ticket['ticket']
            expire = (int(time.time()) + expire) if expire else None
            return expire, token
        return None, None


