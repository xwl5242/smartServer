# -*- coding:utf-8 -*-
import json
import time
import requests
from tools.Utils import Utils
from lxml.etree import HTML
from config.DB import db


CCTV = ['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV5', 'CCTV5+', 'CCTV6', 'CCTV7',
        'CCTV8', 'CCTV9', 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17']
WS_TV = ['广西卫视', '青海卫视', '内蒙古', '湖北卫视', '江西卫视', '四川卫视', '甘肃卫视', '三沙卫视', '河南卫视',
         '陕西卫视', '东南卫视', '天津卫视', '北京卫视', '海峡卫视', '康巴卫视', '广东卫视',
         '金鹰卡通', '重庆卫视', '河北卫视', '内蒙古卫视', '辽宁卫视', '山西卫视', '广东珠江', '新疆卫视', '黑龙江卫视',
         '四川康巴卫视', '西藏藏语卫视', '海南卫视', '吉林卫视', '贵州卫视', '宁夏卫视', '山东卫视', '江苏卫视',
         '深圳卫视', '云南卫视', '安徽卫视', '湖南卫视', '厦门卫视', '兵团卫视', '浙江卫视', '嘉佳卡通', '西藏卫视', '东方卫视']
GAT_TV = ['翡翠台HD', '明珠台HD', '香港开电视', '凤凰中文', '凤凰资讯', 'TVB经典台', '翡翠台简体',
          '明珠台粤语', '凤凰卫视中文台', '香港凤凰卫视资讯台', '凤凰卫视香港台', '香港卫视', '澳门卫视', '台湾卫视']


class HqTV:
    _cctv_url = [('CCTV1', 'cctv1.html'), ('CCTV2', '347.html'), ('CCTV3', 'cctv3.html'),
                 ('CCTV4', 'cctv4.html'), ('CCTV5', 'cctv5.html'), ('CCTV5+', 'cctv5+.html'),
                 ('CCTV6', 'cctv6.html'), ('CCTV7', 'cctv7.html'), ('CCTV8', '353.html'),
                 ('CCTV9', 'cctv9.html'), ('CCTV10', 'cctv10.html'), ('CCTV11', 'cctv11.html'),
                 ('CCTV12', 'cctv12.html'), ('CCTV13', 'cctv13.html'), ('CCTV14', 'cctv14.html'),
                 ('CCTV15', 'cctv15.html'), ('CCTV17', 'cctv17.html')]
    _ws_url = [('湖南卫视', 'hunanweishi.html'), ('浙江卫视', 'zhejiangweishi.html'),
               ('东方卫视', 'dongfangweishi.html'), ('江苏卫视', 'jiangsuweishi.html'),
               ('安徽卫视', 'anhui.html'), ('重庆卫视', 'chongqing-weishi.html'),
               ('北京卫视', 'beijingweishi.html'), ('天津卫视', 'tianjinweishi.html'),
               ('辽宁卫视', 'liaoningweishi.html'), ('江西卫视', 'jiangxiweishi.html'),
               ('黑龙江卫视', 'heilongjiang.html'), ('山东卫视', 'shandongweishi.html'),
               ('云南卫视', 'yunnan.html'), ('四川卫视', 'sichuan.html'), ('四川康巴卫视', 'sctvkbtv.html'),
               ('河南卫视', 'henan.html'), ('广东卫视', 'guangdong.html'),
               ('深圳卫视', 'szws.html'), ('湖北卫视', 'hubei.html'), ('东南卫视', 'fujian.html'),
               ('厦门卫视', 'xiamen.html'), ('海峡卫视', 'fjtv10.html'), ('河北卫视', 'hebei.html'),
               ('吉林卫视', 'jilin.html'), ('广西卫视', 'guangxi.html'), ('山西卫视', 'shanxi.html'),
               ('陕西卫视', 'shanxiweishi.html'), ('内蒙古卫视', 'neimenggu.html'), ('宁夏卫视', 'ningxia.html'),
               ('西藏卫视', 'xizang.html'), ('新疆卫视', 'xinjiang.html'), ('甘肃卫视', 'gansu.html'),
               ('海南卫视', 'lvyou.html'), ('贵州卫视', 'guizhouweishi.html'), ('青海卫视', 'qinghai-weishi.html'),
               ('兵团卫视', 'bingtuan.html'), ('三沙卫视', 'sansha.html'), ('西藏藏语卫视', 'zangyu.html')]
    _gat_url = [('凤凰卫视中文台', 'fhzw.html'), ('香港凤凰卫视资讯台', 'fhzx.html'), ('凤凰卫视香港台', 'fhxg.html'),
                ('香港卫视', 'xgws.html'), ('阳光卫视', 'ygws.html'), ('香港卫视精品台', 'xgwsjp.html'),
                ('香港TVB8', 'tvb-8.html'), ('星空卫视', 'xkws.html'), ('澳视高清', 'aosgq.html'),
                ('澳视澳门台', 'aosam.html'), ('莲花卫视', 'lhws.html'), ('澳门卫视', 'aomen.html'),
                ('台湾台视', 'taishi.html'), ('台湾中视', 'ctv.html'), ('台湾华视', 'cts.html'), ('tvb翡翠卫星台', 'tvbj.html')]

    @staticmethod
    @db
    def fetch(cursor):
        HqTV._fetch_video_id(cursor, HqTV._ws_url, 2)
        HqTV._fetch_video_id(cursor, HqTV._cctv_url, 1)
        HqTV._fetch_video_id(cursor, HqTV._gat_url, 4)

    @staticmethod
    def get_video_url(video_id):
        url = HqTV._get_video_url(video_id)
        if not url:
            return HqTV.get_video_url(video_id)
        return url

    @staticmethod
    @db
    def _get_video_url(cursor, video_id):
        try:
            cursor.execute(f"select * from iptv_video where id={video_id}")
            video = cursor.fetchone()
            if video:
                tv_ids = str(video['tv_video']).split(",")
                # TODO:// 还差一层 video source
                extend_url = 'http://tv.haoqu99.com/e/extend/tv.php?id='
                script_xpath = '//script[contains(text(),"var signal")]/text()'
                resp = requests.get(extend_url + tv_ids[0], headers=Utils.ua())
                if resp and resp.content:
                    root = HTML(str(resp.content, encoding='gbk'))
                    script = root.xpath(script_xpath)
                    if script and len(script) > 0 and 'signal =' in script[0]:
                        script = script[0]
                        script = script[(script.find('signal =') + 8): script.find('var data', script.find('signal ='))]
                        script = str(script).strip().replace('\n', '').replace("'", "")
                        if script and len(script.split("$")) > 1:
                            video_url = script.split("$")[1]
                            if video_url and 'player.521fanli.cn' in video_url:
                                if '.m3u8' in video_url:
                                    return video_url[video_url.index('http', 5):]
                                else:
                                    new_video = ','.join(tv_ids[1:])
                                    cursor.execute(f"update iptv_video set tv_video='{new_video}' where id='{video_id}'")
                                    exception_id = dict(HqTV.get_exception_id())
                                    exception_id = exception_id.get(video['tv_name'], "")
                                    if exception_id:
                                        exists = list(exception_id.split(","))
                                        exists.append(tv_ids[0])
                                        update_id = ','.join(exists)
                                        cursor.execute(f"update iptv_exception_id set exception_id='{update_id}' where tv_name='{video['tv_name']}'")
                                    else:
                                        cursor.execute(f"insert into iptv_exception_id values ('{video['tv_name']}', '{tv_ids[0]}')")
                            else:
                                return video_url
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(repr(e))
            return None

    @staticmethod
    @db
    def get_exception_id(cursor):
        result = {}
        cursor.execute(f"select * from iptv_exception_id")
        exception = cursor.fetchall()
        for e in exception:
            result[e['tv_name']] = e['exception_id']
        return result

    @staticmethod
    def _fetch_video_id(cursor, index_url, index):
        sql = []
        exception_id = dict(HqTV.get_exception_id())
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        base_url = f'http://tv.haoqu99.com/{index}/'
        li_xpath = '//li/span[contains(text(),"#FLAG#")]/parent::li/@data-player'
        for url in index_url:
            if exception_id:
                exception_id = exception_id.get(url[0], "")
            resp = requests.get(base_url + url[1], headers=Utils.ua())
            if resp and resp.content:
                root = HTML(str(resp.content, encoding='gbk'))
                video_id = root.xpath(li_xpath.replace('#FLAG#', 'HD'))
                video_id = root.xpath(li_xpath.replace('#FLAG#', '电信')) if len(video_id) == 0 else video_id
                video_id = root.xpath(li_xpath.replace('#FLAG#', '联通')) if len(video_id) == 0 else video_id
                video_id = root.xpath(li_xpath.replace('#FLAG#', '多线')) if len(video_id) == 0 else video_id
                video_id = list(set(video_id))
                if len(video_id) > 0:
                    video_id = [vi for vi in video_id if vi not in exception_id]
                    video_id = ",".join(video_id)
                    sql.append(f"('1','{url[0]}','{video_id}','{update_time}')")
        cursor.execute('insert into iptv_video(channel,tv_name,tv_video,update_time) values ' + ",".join(sql))

        # @staticmethod
        # def _fetch():
        #     result = []
        #     index_url = 'http://tv.haoqu99.com/4/'
        #     href_xpath = '//ul[@class="p-list-sya"]/li/a/@href'
        #     title_xpath = '//ul[@class="p-list-sya"]/li/a/img/@alt'
        #     resp = requests.get(index_url, headers=Utils.ua())
        #     root = HTML(str(resp.content, encoding='gbk'))
        #     u = root.xpath(href_xpath)
        #     u = [u.replace('/4/', '') for u in u]
        #     t = root.xpath(title_xpath)
        #     for i, uu in enumerate(u):
        #         result.append((t[i], uu))
        #     print(result)


class IpTV:

    @staticmethod
    @db
    def get_video_by_name(cursor, tv_name):
        cursor.execute(f"select id,channel,tv_video from iptv_video where tv_name='{tv_name}'")
        video_list = cursor.fetchall()
        for v in video_list:
            v['tv_video'] = '' if v['channel'] != '1' else v['tv_video']
        return video_list

    @staticmethod
    @db
    def get_video_url(cursor, video_id):
        try:
            cursor.execute(f"select * from iptv_video where id={video_id}")
            video = cursor.fetchone()
            if video:
                return video['tv_video']
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(repr(e))
            return None

    @staticmethod
    @db
    def fetch(cursor):
        video_url, sql = [], []
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        exclude = ['TVBJ2', '无线新闻台', '无线财经台', 'VIUHD', 'viu6', 'RTHK31', 'RTHK32', 'now新闻', '美亚粤语',
                   '美亚普通话', '天映经典粤语', '天映经典普通话', 'animax第一声道', 'animax原声', 'Hands Up Channel',
                   'Hands Up Channel(第2声道),', 'Thrill', 'Thrill(第2声道)', 'TVB为食台', 'TVB为食台(第2声道)',
                   'TVB星河(粤语)', 'TVB星河(普通话)', 'TVB功夫台(粤语)', 'TVB功夫(普通话)', 'Discovery', '动物星球',
                   'Love Nature 4K', 'Love Nature 4K(第2声道)', 'VIU粤语', 'CGTN']
        url = 'http://cms.cmsiptv.xyz:8064/basis/communityApp/tvLiveList?authCode=&liveClass='
        for i in range(1, 4):
            resp = requests.get(url+str(i), headers=Utils.ua())
            video_url.extend(IpTV._parse(resp))
        video_url = [u for u in video_url if u[0] not in exclude]
        for v in video_url:
            sql.append(f"('2','{v[0]}','{v[1]}','{update_time}')")
        cursor.execute('insert into iptv_video(channel,tv_name,tv_video,update_time) values ' + ",".join(sql))

    @staticmethod
    def _parse(resp):
        urls = []
        if resp and resp.text:
            resp = json.loads(resp.text)
            if resp and resp['data'] and len(resp['data']) > 0:
                for video in resp['data']:
                    video_name = video['liveName']
                    video_address = video['liveAddress']
                    urls.append((video_name, video_address))
        return urls


class HdTV:
    @staticmethod
    @db
    def get_video_url(cursor, video_id):
        try:
            cursor.execute(f"select * from iptv_video where id={video_id}")
            video = cursor.fetchone()
            if video:
                url = "http://hd181.com/"
                resp = requests.get(url + video['tv_video'], headers=Utils.ua())
                if resp and resp.content:
                    root = HTML(str(resp.content, encoding='utf8'))
                    video = root.xpath('//source/@src')
                    if video and len(video) > 0:
                        return video[0]
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(repr(e))
            return None

    @staticmethod
    @db
    def fetch(cursor):
        result, sql = [], []
        url = "http://hd181.com/"
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        href_xpath = '//div[@class="item item-#INDEX#"]/ul/li/a/@href'
        title_xpath = '//div[@class="item item-#INDEX#"]/ul/li/a/@title'
        for index in range(1, 3):
            resp = requests.get(url, headers=Utils.ua())
            if resp and resp.content:
                root = HTML(str(resp.content, encoding='utf8'))
                urls = root.xpath(href_xpath.replace('#INDEX#', str(index)))
                titles = root.xpath(title_xpath.replace('#INDEX#', str(index)))
                for i, t in enumerate(titles):
                    result.append((t.replace('直播', ''), urls[i]))
        for v in result:
            if v[0] not in ['cctv4亚洲', 'cctv4美洲', 'cctv4欧洲']:
                video_name = v[0].replace('cctv', 'CCTV').replace('台湾三立', '台湾卫视')
                sql.append(f"('3','{video_name}','{v[1]}','{update_time}')")
        cursor.execute('insert into iptv_video(channel,tv_name,tv_video,update_time) values ' + ",".join(sql))


