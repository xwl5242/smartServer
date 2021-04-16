# -*- coding:utf-8 -*-
import os
import json
import random
import requests
from hashlib import md5
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
        file_no, url = self._one()
        if not file_no:
            return self.one()
        return file_no, url

    def _one(self):
        file_dir = os.path.join(os.path.dirname(__file__), 'mv')
        url = self._request(self.key)
        url = url if url else self._request(self.token())
        if url:
            file_uuid = md5(url.encode('utf8')).hexdigest()
            file_path = os.path.join(file_dir, f'{file_uuid}.mp4')
            file_re_path = os.path.join(file_dir, f'{file_uuid}.re')
            if not os.path.exists(file_path):
                resp = requests.get(url, headers={'User-Agent': random.choice(Conf.UAS)})
                if resp and resp.content:
                    with open(file_path, 'wb') as fw:
                        fw.write(resp.content)
                    with open(file_re_path, 'w') as frw:
                        frw.write(url)
                    return file_uuid, url
            else:
                with open(file_re_path, 'r') as f:
                    url = f.read()
                return file_uuid, url
        return None, None

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

