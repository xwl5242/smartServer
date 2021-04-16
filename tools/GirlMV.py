# -*- coding:utf-8 -*-
import json
import random
import requests
from config.Config import Conf


class GirlMV:
    def __init__(self):
        """
        美女随机小视频
        """
        self.m = 'xwlzhx2015111821'
        self.key = '8e4950c95bd8cd993f0262ecff216157'
        self.token_url = 'http://www.666api.cn/api/token.php'
        self.api_url = 'http://www.666api.cn/apidoc/api/meinv.php?&token_key='

    def one(self):
        url = self._request(self.key)
        return url if url else self._request(self.token())

    def _request(self, token):
        resp = requests.get(self.api_url + token, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            return json.loads(resp.text)['url']
        return None

    def token(self):
        resp = requests.post(self.token_url, {
            'user_name': 'root'
        }, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            return json.loads(resp.text)['token']
        return None


if __name__ == '__main__':
    print(GirlMV().one())


