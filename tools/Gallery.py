# -*- coding:utf-8 -*-
import json
import requests
from tools.Smart import Smart
from config.Config import Conf
from random import choice, shuffle


class Gallery:

    @staticmethod
    def gif(page_no):
        return Smart.gif_query(page_no)

    @staticmethod
    def gif_fetch():
        key = 'a6919e2c02e0891115be46ef57e3396c'
        for index in range(1, 3100):
            url = f'https://way.jd.com/showapi/dtgxt?page={index}&maxResult=20&appkey={key}'
            resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
            if resp and resp.text:
                resp = json.loads(resp.text)
                if int(resp['code']) == 10000 and resp['result']:
                    resp = resp['result']
                    if resp and resp['showapi_res_body'] and resp['showapi_res_body']['contentlist']:
                        gif_list = resp['showapi_res_body']['contentlist']
                        if gif_list and len(gif_list) > 0:
                            for gif in gif_list:
                                Smart.gif_save(gif['id'], gif['title'], gif['img'])
                        else:
                            break

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

    @staticmethod
    def wallpaper_download(url):
        resp = requests.get(url, headers={"User-Agent": choice(Conf.UAS)})
        if resp and resp.content:
            import os, uuid
            file_no = str(uuid.uuid4())
            file_path = os.path.join(os.path.dirname(__file__), 'mv', f'{file_no}.png')
            with open(file_path, 'wb') as f:
                f.write(resp.content)
            return file_no
        return None


if __name__ == '__main__':
    print(Gallery.gif(1))

