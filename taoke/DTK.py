# -*- coding:utf-8 -*-
import operator
import hashlib
import copy
import subprocess
import logging
import json
from config.DB import db
from config.Config import Conf
logging.captureWarnings(True)
# noinspection PyBroadException
try:
    import requests
except Exception:
    print('尚未安装requests库，正在安装，请稍后！')
    subprocess.call('pip install requests')
    print('requests库安装成功！第一次调用接口！')
    import requests


class DTKService:
    @staticmethod
    def universal_parse(content):
        """
        淘系万能解析
        :param content:
        :return:
        """
        good_json = DTKService._send('TB_UNIVERSAL_PARSE', {'content': content})
        # {'commissionRate': 3.1, 'commissionType': 'COMMON', 'goodsId': '633240667694'}
        return good_json['data'] if (good_json and good_json['code'] == 0) else None

    @staticmethod
    def privilege_link(goods_id):
        """
        高效转链
        :param goods_id:
        :return:
        """
        link = DTKService._send('PRIVILEGE_LINK', {'goodsId': goods_id})
        flag = link and link['code'] == 0 and link['data'] and link['data']['shortUrl']
        return link['data']['shortUrl'] if flag else None

    @staticmethod
    def goods_detail(goods_id):
        """
        商品详情
        :param goods_id: 淘宝商品id
        :return:
        """
        good_json = DTKService._send('GOODS_DETAIL', {'goodsId': goods_id})
        return good_json['data'] if (good_json and good_json['code'] == 0) else None

    @staticmethod
    def tao_twd_create(text, url):
        """
        生成淘口令
        :param text:
        :param url:
        :return:
        """
        twd_json = DTKService._send('TB_PASSWD_CREATE', {'text': text, 'url': url})
        # {'password_simple': '￥fkCpcJlsI6W￥', 'model': '10￥fkCpcJlsI6W￥/', 'longTpwd': '108.0￥fkCpcJlsI6W￥...'}
        return twd_json['data'] if (twd_json and twd_json['code'] == 0) else None

    @staticmethod
    def tao_twd_to_twd(content):
        """
        淘口令转淘口令（转为自己的淘口令）
        :param content:
        :return:
        """
        passwd_json = DTKService._send('TB_TWD_TO_TWD', {'content': content})
        # {'password_simple': '￥fkCpcJlsI6W￥', 'model': '10￥fkCpcJlsI6W￥/', 'longTpwd': '108.0￥fkCpcJlsI6W￥...'}
        return passwd_json['data'] if (passwd_json and passwd_json['code'] == 0) else None

    @staticmethod
    def _send(api_key, args):
        """
        DTK API 请求
        :param api_key:
        :param args:
        :return:
        """
        url, method, version = DTKService._get_dtk_api(api_key)
        if url and method and version:
            params = {'version': version}
            params.update(args)
            return DtkOpenPlatform.send(method, url, params)
        return None

    @staticmethod
    @db
    def _get_dtk_api(cursor, api_key):
        """
        根据API_KEY查询DTK API
        :param cursor:
        :param api_key:
        :return:
        """
        sql = f"select * from dtk_api where api_key='{api_key}' and del_flag='0'"
        cursor.execute(sql)
        api = cursor.fetchone()
        if api and api['api_req_url'] and api['api_req_method'] and api['api_version']:
            return api['api_req_url'], api['api_req_method'], api['api_version']
        return None, None, None


class DtkOpenPlatform:
    @staticmethod
    def md5(arg):
        md5 = hashlib.md5()
        loc_bytes_utf8 = arg.encode(encoding="utf-8")
        md5.update(loc_bytes_utf8)
        return md5.hexdigest()

    @staticmethod
    def md5_sign(args=None, key=None):
        copy_args = copy.deepcopy(args)
        sorted_args = sorted(copy_args.items(), key=operator.itemgetter(0))
        tmp = []
        for i in sorted_args:
            tmp.append('{}={}'.format(list(i)[0], list(i)[1]))
        sign = DtkOpenPlatform.md5('&'.join(tmp) + '&' + 'key={}'.format(key)).upper()
        copy_args['sign'] = sign
        return copy_args

    @staticmethod
    def send(method, url, args, secret=Conf.DTK_APP_SECRET, user_agent=None, content_type=None, data_type='data'):
        if not user_agent:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/68.0.3440.84 Safari/537.36",
                       'Content-Type': content_type}
        else:
            headers = {"User-Agent": user_agent, 'Content-Type': content_type}
        params = {
            'appKey': Conf.DTK_APP_KEY
        }
        params.update(args)
        data = DtkOpenPlatform.md5_sign(args=params, key=secret)
        method_tmp = method.lower()
        if method_tmp == 'get':
            response = requests.request(method=method_tmp, url=url, params=data, headers=headers, verify=False).json()
            return response
        elif method_tmp == 'post':
            if data_type == 'data':
                response = requests.request(method=method_tmp, url=url, data=data, headers=headers, verify=False).json()
                return response
            elif data_type == 'json':
                response = requests.request(method=method_tmp, url=url, data=json.dumps(data), headers=headers, verify=False).json()
                return response


