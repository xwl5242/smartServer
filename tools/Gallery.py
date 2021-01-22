# -*- coding:utf-8 -*-
import json
import requests
from urllib.parse import quote
from random import choice, shuffle
from config.Config import Conf


class Gallery:

    @staticmethod
    def gif(page_no):
        arr = [0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1]
        if choice(arr) == 0:
            ret = Gallery._gif_query(page_no)
            return ret if ret and len(ret) > 0 else Gallery._gif_hot(page_no)
        else:
            return Gallery._gif_hot(page_no)

    @staticmethod
    def _gif_query(page_no):
        hot_word_url = "https://www.soogif.com/hotword"
        resp0 = requests.get(hot_word_url, headers={"User-Agent": choice(Conf.UAS)})
        if resp0 and resp0.content:
            resp0 = json.loads(resp0.content, encoding='utf-8')
            if resp0['code'] == 0 and resp0['data'] \
                    and resp0['data']['list'] and len(resp0['data']['list']) > 0:
                cur_query = quote(choice(resp0['data']['list'])['query'])
                if cur_query:
                    url = f"https://www.soogif.com/material/query?query={cur_query}&sortField=&start={page_no*20}&size=20&imageType=0"
                    resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
                    if resp and resp.content:
                        resp = json.loads(resp.content, encoding='utf-8')
                        if resp['code'] == 0 and resp['data'] \
                                and resp['data']['list'] and len(resp['data']['list']) > 0:
                            gif_list = resp['data']['list']
                            return [{'url': str(gif['url']).replace("http://", 'https://'), 'title': gif['subText']} for gif in gif_list]
        return []

    @staticmethod
    def _gif_hot(page_no):
        url = f"https://www.soogif.com/hotGif?start={page_no * 20}&size=20"
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            resp = json.loads(resp.content, encoding='utf-8')
            if resp['code'] == 0 and resp['data'] \
                    and resp['data']['result'] and len(resp['data']['result']) > 0:
                gif_list = resp['data']['result']
                return [{'url': str(gif['gifurl']).replace('http://', 'https://'), 'title': gif['title']} for gif in gif_list]
        return []

    @staticmethod
    def wallpaper_type():
        colors = ['#ED5736', '#F00056', '#F47983', '#F20C00', '#FF2121',
                  '#C83C23', '#FF4C00', '#FF4E20', '#F35336', '#CB3A56',
                  '#FF2D51', '#C91F37', '#FF3300', '#DC3023', '#F9906F',
                  '#ED5A65', '#EE3F4D', '#C02C38', '#A61B29', '#D11A2D',
                  '#C21F30', '#DE1C31', '#EF475D', '#ED556A', '#F03752',
                  '#EE2746', '#EE4863', '#EE4866', '#CC163A', '#BF3553',
                  '#EC2C64', '#EB507E', '#EB3C70', '#EA517F', '#ED2F6A',
                  '#EF3473', '#E16C96', '#D13C74', '#EC4E8A', '#DE3F7C',
                  '#EE2C79', '#EF498B', '#EC2D7A',  '#D2357D']
        shuffle(colors)
        url = f"https://api.mlwei.com/wallpaper/api/?cid=tags"
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            resp = json.loads(resp.content, encoding='utf-8')
            if resp['errno'] == '0' and resp['data'] and len(resp['data']) > 0:
                resp = resp['data']
                tmp_colors = colors[0: len(resp)]
                return [{'id': wp['id'], 'name': wp['name'], 'color': tmp_colors[i]} for i, wp in enumerate(resp)]

    @staticmethod
    def wallpaper_list(t, page_no):
        page_no = int(page_no) if page_no else 0
        url = f"https://api.mlwei.com/wallpaper/api/?cid={t}&start={page_no*10}&count=10"
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
                                or str(wk) == 'resolution' or str(wk) == 'url' or str(wk) == 'utag':
                            temp[wk] = str(wp[wk]).strip().replace(" ", "").replace("http://", "https://")
                    result.append(temp)
                return result
        return []


if __name__ == '__main__':
    print(Gallery.wallpaper_type())

