# -*- coding:utf-8 -*-
import json
import random
import requests
from config.Config import Conf


class CHP:

    @staticmethod
    def chp():
        return CHP._req_get('https://chp.shadiao.app/api.php')

    @staticmethod
    def tg():
        resp = json.loads(CHP._req_get('https://xiaojieapi.cn/API/tiangou.php'))
        if resp and resp['code'] == 1000:
            return resp['text']
        return "你就是彩虹屁"

    @staticmethod
    def _req_get(url):
        try:
            resp = requests.get(url, headers={'User-Agent': random.choice(Conf.UAS)})
            if resp and resp.text:
                return resp.text
        except:
            import traceback
            traceback.print_exc()
        return "你就是彩虹屁"


