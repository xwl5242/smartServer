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

    UAS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"
    ]

