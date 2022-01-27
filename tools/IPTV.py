# -*- coding:utf-8 -*-
import json
import time
import requests
from config.DB import db
from tools.Utils import Utils
from fake_useragent import UserAgent


CCTV = ['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV5', 'CCTV5+', 'CCTV6', 'CCTV7',
        'CCTV8', 'CCTV9', 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17']
WS_TV = ['东方卫视', '浙江卫视', '湖南卫视', '北京卫视', '黑龙江卫视', '东南卫视', '山东卫视', '广东卫视',
         '湖北卫视', '四川卫视', '辽宁卫视', '安徽卫视', '深圳卫视', '天津卫视', '重庆卫视', '河南卫视',
         '河北卫视', '江苏卫视', '江西卫视', '广西卫视', '内蒙古卫视', '山西卫视', '康巴卫视', '陕西卫视',
         '宁夏卫视', '青海卫视', '海南卫视', '云南卫视', '新疆卫视', '西藏卫视', '甘肃卫视', '金鹰卡通', '嘉佳卡通', '广东珠江']
GAT_TV = ['翡翠台', '明珠台', '香港HKS', '凤凰中文', '凤凰资讯', 'TVB经典台', '澳门卫视']


class IpTV:

    @staticmethod
    def get_tv_channel():
        return {'cctv': CCTV, 'ws_tv': WS_TV, 'GAT_TV': GAT_TV}

    @staticmethod
    def get_tv_channel_id():
        channel = {}
        for i, tv in enumerate(CCTV):
            channel[tv] = f"1-{i}"
        for i, tv in enumerate(WS_TV):
            channel[tv] = f"2-{i}"
        for i, tv in enumerate(GAT_TV):
            channel[tv] = f"3-{i}"
        return channel

    @staticmethod
    def fetch():
        xj = IpTV._fetch_xj()
        xh = IpTV._fetch_xh()
        channel_info = IpTV.get_tv_channel_id()
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        for tv in channel_info.keys():
            urls = []
            if xj.get(tv, ""):
                urls.append(xj[tv])
            if xh.get(tv, ""):
                urls.extend(xh[tv].split('$'))
            urls = urls[0: 11] if len(urls) > 10 else urls
            insert_sql_values = []
            for index, url in enumerate(urls):
                insert_sql_values.append(f"('{channel_info[tv]}','{tv}','{url}',{index+1},'{update_time}')")
            Service.delete_videos_by_id(channel_info[tv])
            Service.insert_videos(insert_sql_values)

    @staticmethod
    def _fetch_xj():
        tv_dict = {}
        url = 'http://cms.cmsiptv.xyz:8064/basis/communityApp/tvLiveList?authCode=&liveClass='
        for i in range(1, 4):
            resp = requests.get(url + str(i), headers=Utils.ua())
            if resp and resp.text:
                resp = json.loads(resp.text)
                if resp and resp['data'] and len(resp['data']) > 0:
                    for video in resp['data']:
                        video_name = video['liveName']
                        video_address = video['liveAddress']
                        if i == 3:
                            video_name = "翡翠台" if video_name == '翡翠台HD' else video_name
                            video_name = "明珠台" if video_name == '明珠台HD' else video_name
                            video_name = "香港HKS" if video_name == '香港开电视' else video_name
                        else:
                            video_name = "内蒙古卫视" if video_name == '内蒙古' else video_name
                        if video_name in CCTV or video_name in WS_TV or video_name in GAT_TV:
                            tv_dict[video_name] = video_address
        return tv_dict

    @staticmethod
    def _fetch_xh():
        tv_dict = {}
        resp = requests.get('http://fj365.ml/m.json', headers={'User-Agent': UserAgent().random})
        if resp and resp.text:
            resp = resp.text
            resp = '\n'.join([line for line in resp.split('\n') if line.replace(" ", '').find('//') != 0])
            lives = json.loads(resp)['lives']
            for tv in lives:
                for channel in tv['channels']:
                    channel_name = channel['name'].replace('-', '').replace('HD', '').replace('hd', '')
                    if channel_name in CCTV or channel_name in WS_TV or channel_name in GAT_TV:
                        url = '$'.join([u for u in channel['urls'] if '.m3u8' in u])
                        if tv_dict.get(channel_name, ""):
                            tv_dict[channel_name] = tv_dict[channel_name] + '$' + url
                        else:
                            tv_dict[channel_name] = url
        return tv_dict

    @staticmethod
    def get_video_url(video_id):
        try:
            tv_list = Service.get_video_by_id(video_id)
            return [u['tv_url'] for u in tv_list]
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(repr(e))
            return None


class Service:
    @staticmethod
    @db
    def get_iptv_config(cursor, ver):
        cursor.execute(f"select * from iptv_config where ver='{ver}'")
        return cursor.fetchone()

    @staticmethod
    @db
    def get_video_by_id(cursor, video_id):
        cursor.execute(f"select * from iptv_video where tv_id='{video_id}' order by seq asc")
        return cursor.fetchall()

    @staticmethod
    @db
    def insert_videos(cursor, values_sql):
        cursor.execute('insert into iptv_video(tv_id,tv_name,tv_url,seq,update_time) values ' + ",".join(values_sql))

    @staticmethod
    @db
    def delete_videos_by_id(cursor, tv_id):
        cursor.execute(f"delete from iptv_video where tv_id='{tv_id}'")

