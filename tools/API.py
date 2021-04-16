# -*- coding:utf-8 -*-
import os
import json
import random
import requests
from config.Config import Conf


class API:

    @staticmethod
    def menus():
        menus_path = os.path.join(os.path.dirname(__file__), 'menus')
        with open(menus_path, 'r', encoding='utf-8') as fr:
            return json.loads(fr.read())

    @staticmethod
    def love():
        return API._req_free('https://v1.alapi.cn/api/qinghua', 'content')

    @staticmethod
    def garbage(goods):
        return API._req_get(f'https://api.66mz8.com/api/garbage.php?name={goods}')

    @staticmethod
    def short_url(url):
        dwz_list = ['wechat', 'urlcn', 'tcn', 'sinaurl', 'suoim', 'suonz', 'mrwso']
        dwz = random.choice(dwz_list)
        return API._req_get(f'https://api.66mz8.com/api/short.php?dwz={dwz}&url={url}')

    @staticmethod
    def article():
        url = 'https://v1.alapi.cn/api/mryw/random'
        resp = requests.get(url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp['code'] == 200:
                return resp['data']
        return None

    @staticmethod
    def word():
        k = random.choice(["a", "b", "c", "d", "e", "f", "g"])
        url_list = ['https://v1.alapi.cn/api/soul@@@title', 'https://api.66mz8.com/api/quotation.php@@@NO',
                    'https://chp.shadiao.app/api.php@@@NO', f'https://v1.alapi.cn/api/hitokoto?type={k}@@@hitokoto']
        url = random.choice(url_list)
        url, key = url.split('@@@')[0], url.split('@@@')[1]
        if key == 'NO':
            return API._req_get(url)
        else:
            return API._req_free(url, key)

    @staticmethod
    def _req_free(url, key):
        resp = requests.get(url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp['code'] == 200:
                return resp['data'][key]
        return None

    @staticmethod
    def _req_get(url):
        resp = requests.get(url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            return resp.text
        return "你就是彩虹屁"


if __name__ == '__main__':
    print(API.word())

