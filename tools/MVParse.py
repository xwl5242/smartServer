# -*- coding:utf-8 -*-
import re
import os
import json
import random
import requests
from hashlib import md5
from random import choice
from config.Config import Conf
from util.NeteaseUtil import NeteaseUtil as Nu


class MVParse:
    def __init__(self, url):
        """
        各平台小视频解析
        """
        self.url = url
        self.m_key = 'important-151118'
        self.ppx = 'https://v1.alapi.cn/api/video/ppx?url='
        self.dy = 'https://v1.alapi.cn/api/video/dy?url='
        self.jh = 'https://v1.alapi.cn/api/video/jh?url='

    def parse(self, mv_type):
        file_no = Nu.aes_encrypt(self.m_key, self.url)
        file_no = md5(file_no.encode('utf8')).hexdigest()
        file_dir = os.path.join(os.path.dirname(__file__), 'mv')
        file_path = os.path.join(file_dir, f'{file_no}.mp4')
        file_re_path = os.path.join(file_dir, f'{file_no}.re')
        if not os.path.exists(file_path):
            v_url, c_url = self._parse(mv_type)
            if v_url and c_url:
                resp = requests.get(v_url, headers={'User-Agent': random.choice(Conf.UAS)})
                if resp and resp.content:
                    with open(file_path, 'wb') as fb:
                        fb.write(resp.content)
                    with open(file_re_path, 'w') as fw:
                        fw.write(c_url)
                    return file_no, c_url
        else:
            with open(file_re_path, 'r') as r:
                c_url = r.read()
            return file_no, c_url
        return None

    def _parse(self, mv_type):
        if mv_type == 'ppx':
            data = self.ppx_parse()
        elif mv_type == 'dy':
            data = self.dy_parse()
        else:
            data = self.jh_parse()
        if data:
            return data['video_url'], data['cover_url']
        return None, None

    def ppx_parse(self):
        resp = requests.get(self.ppx+self.url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp['code'] == 200:
                return resp['data']
            else:
                return self.jh_parse()
        return None

    def dy_parse(self):
        resp = requests.get(self.dy+self.url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp['code'] == 200:
                return resp['data']
            else:
                data = self.jh_parse()
                return data if data else DouYin.parse(self.url)
        return None

    def jh_parse(self):
        resp = requests.get(self.jh + self.url, headers={'User-Agent': random.choice(Conf.UAS)})
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp['code'] == 200:
                return resp['data']
        return None


class DouYin:
    @staticmethod
    def parse(v_url):
        r = requests.head(v_url)
        v_id = re.findall(r'/video/(\d{19})/', r.headers['Location'])[0]
        if v_id:
            play_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={v_id}'
            res_json = requests.get(play_url, headers={'User-Agent': choice(Conf.UAS)}).json()
            video_json = res_json['item_list'][0]['video']
            # music_json = res_json['item_list'][0]['music']
            video_url = str(video_json['play_addr']['url_list'][0]).replace('playwm', 'play')
            # music_url = str(music_json['play_url']['url_list'][0])
            return video_url, video_json['origin_cover']['url_list'][0]
        return None, None


if __name__ == '__main__':
    print(MVParse('https://h5.pipix.com/s/uW4KXh/').parse('ppx'))


