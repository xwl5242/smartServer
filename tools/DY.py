# -*- coding:utf-8 -*-
import re
import os
import json
import requests
from random import choice
from config.Config import Conf


class DouYin:

    @staticmethod
    def parse(v_url):
        try:
            r = requests.head(v_url)
            v_id = re.findall(r'/video/(\d{19})/', r.headers['Location'])[0]
            file_dir = os.path.join(os.path.dirname(__file__), 'mv')
            if v_id:
                if not os.path.exists(os.path.join(file_dir, f'{v_id}.mp4')):
                    # share_url = f'https://www.iesdouyin.com/share/video/{v_id}/?region=CN&mid={v_id}'
                    # html = requests.get(share_url, headers={'User-Agent': choice(Conf.UAS)}).text
                    # dy_tk = re.findall(r'dytk: "(\w{64})"', html)[0]
                    play_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={v_id}'
                    res_json = requests.get(play_url, headers={'User-Agent': choice(Conf.UAS)}).json()
                    video_json = res_json['item_list'][0]['video']
                    music_json = res_json['item_list'][0]['music']
                    video_url = str(video_json['play_addr']['url_list'][0]).replace('playwm', 'play')
                    music_url = str(music_json['play_url']['url_list'][0])
                    if video_url:
                        v_file_path = os.path.join(file_dir, f'{v_id}.mp4')
                        d_file_path = os.path.join(file_dir, f'{v_id}.re')
                        import time
                        time.sleep(1)
                        v_resp = requests.get(video_url, headers={'User-Agent': choice(Conf.UAS)})
                        with open(v_file_path, 'wb') as fb:
                            fb.write(v_resp.content)
                        res = {
                            'id': v_id,
                            'pic': video_json['origin_cover']['url_list'][0],
                            'music': music_url
                        }
                        with open(d_file_path, 'w') as fw:
                            fw.write(json.dumps(res, ensure_ascii=False, indent=2))
                return v_id
        except:
            import traceback
            traceback.print_exc()
            return None


if __name__ == '__main__':
    DouYin.parse('https://v.douyin.com/ErAB1J')

