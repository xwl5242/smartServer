# -*- coding:utf-8 -*-
import os
from configparser import ConfigParser


class Conf:
    _config = ConfigParser()
    _config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
    # mysql 数据库相关
    DB_PT = _config.get('db', 'plat')
    DB_HOST = _config.get(f'db_{DB_PT}', 'host')
    DB_PORT = int(_config.get(f'db_{DB_PT}', 'port'))
    DB_USER = _config.get(f'db_{DB_PT}', 'user')
    DB_PASSWORD = _config.get(f'db_{DB_PT}', 'password')
    DB_DATABASE = _config.get(f'db_{DB_PT}', 'database')
    # wx公众平台相关
    WX_APP_ID = _config.get('wechat', 'app_id')
    WX_APP_SECRET = _config.get('wechat', 'app_secret')
    WX_MSG_TOKEN = _config.get('wechat', 'msg_token')
    WX_MSG_AES_KEY = _config.get('wechat', 'msg_aes_key')
    # 百度机器人相关
    BOT_URL = _config.get('bd_bot', 'bot_url')
    BOT_OAUTH_URL = _config.get('bd_bot', 'oauth_url')
    BOT_API_KEY = _config.get('bd_bot', 'api_key')
    BOT_API_SECRET = _config.get('bd_bot', 'api_secret')
    BOT_SERVICE_ID = _config.get('bd_bot', 'service_id')
    # 腾讯AI相关
    TENCENT_AI_SECRET_ID = _config.get('tencent', 'secret_id')
    TENCENT_AI_SECRET_KEY = _config.get('tencent', 'secret_key')
    # 大淘客相关
    DTK_APP_KEY = _config.get('dtk', 'app_key')
    DTK_APP_SECRET = _config.get('dtk', 'app_secret')
    # 微信消息回复地址
    WX_REPLY_TPL_URL = _config.get(f'wx_msg_{DB_PT}', 'reply_tpl_url')


