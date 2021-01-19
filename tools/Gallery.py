# -*- coding:utf-8 -*-
import json
import requests
from random import choice
from config.Config import Conf


class Gallery:

    @staticmethod
    def gif(page_no):
        page_no = int(page_no)
        url = f"https://www.soogif.com/hotGif?start={page_no*20}&size=20"
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            resp = json.loads(resp.content, encoding='utf-8')
            if resp['code'] == 0 and resp['data'] \
                    and resp['data']['result'] and len(resp['data']['result']) > 0:
                gif_list = resp['data']['result']
                return [{'url': gif['gifurl'], 'title': gif['title']} for gif in gif_list]

    @staticmethod
    def wallpaper_type():
        url = f"https://api.mlwei.com/wallpaper/api/?cid=tags"
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            resp = json.loads(resp.content, encoding='utf-8')
            if resp['errno'] == '0' and resp['data'] and len(resp['data']) > 0:
                resp = resp['data']
                return [{'id': wp['id'], 'name': wp['name']} for wp in resp]

    @staticmethod
    def wallpaper_list(t, page_no):
        url = f"https://api.mlwei.com/wallpaper/api/?cid={t}&start={page_no}&count=2"
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            resp = json.loads(resp.content, encoding='utf-8')
            if resp['errno'] == '0' and resp['data'] and len(resp['data']) > 0:
                resp = resp['data']
                result = []
                for wp in resp:
                    temp = {}
                    for wk in wp.keys():
                        if str(wk).find('img_') == 0 or str(wk) == 'id' \
                                or str(wk) == 'resolution' or str(wk) == 'url':
                            temp[wk] = wp[wk]
                    result.append(temp)
                return result
        return None


if __name__ == '__main__':
    print(Gallery.wallpaper_list(6, 0))

