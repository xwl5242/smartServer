# -*- coding:utf-8 -*-
import time
import uuid
import random
import requests
from lxml import etree
from config.DB import vip_db
from config.Config import Conf


class YTV:

    SQL = 'vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks,' \
          'vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_play_from,vod_time,vod_serial'

    DETAIL = 'vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks,' \
             'vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_time_add,' \
             'vod_content,vod_play_note,vod_play_from,vod_play_url,vod_serial'

    @staticmethod
    @vip_db
    def pre_update_slide(cursor):
        pre_up_sql = "update mac_vod set vod_level=0 where vod_level=5"
        cursor.execute(pre_up_sql)

    @staticmethod
    @vip_db
    def update_slide(cursor, kw, img_url):
        sel_sql = f"select vod_id from mac_vod where vod_name like '%{kw}%'"
        cursor.execute(sel_sql)
        vod_list = cursor.fetchall()
        if vod_list and len(vod_list) > 0:
            for vod in vod_list:
                up_sql = f"update mac_vod set vod_pic_slide='{img_url}', vod_level=5 where vod_id={int(vod['vod_id'])}"
                cursor.execute(up_sql)

    @staticmethod
    @vip_db
    def get_vod_total(cursor):
        sql = "select count(1) total from mac_vod"
        cursor.execute(sql)
        total = cursor.fetchone()
        return total['total'] if total else 0

    @staticmethod
    @vip_db
    def get_vod_update(cursor):
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        now = int(time.mktime(time.strptime(now, '%Y-%m-%d')))
        sql = f"select count(1) total from mac_vod where vod_time_add > {now}"
        cursor.execute(sql)
        total = cursor.fetchone()
        return total['total'] if total else 0

    @staticmethod
    def get_mv_type_list(mv_type, page_no, page_size, ver):
        result = {}
        sub_types = Conf.mv_sub_type().get(mv_type)
        for sub_type in sub_types:
            mvs = YTV.get_mv_by_type(sub_type, page_no, page_size, ver)
            result[sub_type] = mvs
        return result

    @staticmethod
    @vip_db
    def get_mv_type(cursor):
        sql = "select type_id,type_name,type_sort,type_pid from mac_type where type_status='1'  " \
              "and type_id not in (11, 21) and type_mid='1'"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_news(cursor, ver):
        mv_list = []
        top_list = Top().spider()
        # top_list = ['奔跑吧 第五季']
        for top in top_list:
            if str(top).find(' ') > 0:
                tt = top.split(' ')[0]
                tt1 = top.split(' ')[1]
            elif str(top).find('·') > 0:
                tt = top.split('·')[0]
                tt1 = top.split('·')[1]
            else:
                tt = top
                tt1 = top
            sql = f"select {YTV.SQL} from mac_vod " \
                  f"where vod_status='1' and type_id not in (11, 21) and " \
                f"vod_name like '{tt}%' order by vod_time_add desc limit 0,9"
            cursor.execute(YTV.get_real_sql(cursor, ver, sql))
            mvs = cursor.fetchall()
            if mvs and len(mvs) > 1:
                for mv in mvs:
                    if str(mv['vod_name']).find(tt1) > 0:
                        mv_list.append(mv)
            else:
                mv_list.extend(mvs)
        return mv_list

    @staticmethod
    @vip_db
    def get_mv_by_type(cursor, mv_type, page_no, page_size, ver):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select {YTV.SQL} from mac_vod where vod_status='1' and type_id={mv_type} " \
            f"and type_id not in (11, 21) order by vod_time_add desc limit {page_no * page_size},{page_size}"
        cursor.execute(YTV.get_real_sql(cursor, ver, sql))
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_by_type_count(cursor, mv_type):
        sql = f"select count(1) total from mac_vod where vod_status='1' " \
            f"and type_id not in (11, 21) and type_id={mv_type}"
        cursor.execute(sql)
        total = cursor.fetchone()
        return total['total'] if total else 0

    @staticmethod
    @vip_db
    def get_mv_by_dy(cursor, page_no, page_size, ver):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select {YTV.SQL} from mac_vod where vod_status='1' and type_id not in (11, 21) " \
            f"and type_id between 6 and 12 order by vod_time_add desc limit {page_no * page_size},{page_size}"
        cursor.execute(YTV.get_real_sql(cursor, ver, sql))
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_by_ds(cursor, page_no, page_size, ver):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select {YTV.SQL} from mac_vod where vod_status='1' and type_id not in (11, 21) " \
            f"and type_id between 13 and 16 order by vod_time_add desc limit {page_no * page_size},{page_size}"
        cursor.execute(YTV.get_real_sql(cursor, ver, sql))
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_detail(cursor, mv_id, ver):
        sql = f"select {YTV.DETAIL} from mac_vod where vod_status='1' and vod_id={mv_id}"
        cursor.execute(YTV.get_real_sql(cursor, ver, sql))
        return cursor.fetchone()

    @staticmethod
    @vip_db
    def get_mv_by_name(cursor, tv_name, ver):
        sql = f"select {YTV.SQL} from mac_vod where vod_status='1' " \
            f"and type_id not in (11, 21) and vod_name like '%{tv_name}%' order by vod_time_add desc"
        cursor.execute(YTV.get_real_sql(cursor, ver, sql))
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_settings(cursor, ver):
        sql = f"select * from mac_settings where version='{ver}'"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    def get_real_sql(cursor, ver, query):
        sql = f"select show_vods,status from mac_settings where version='{ver}'"
        cursor.execute(sql)
        mv = cursor.fetchone()
        id_list = "','".join(str(mv['show_vods']).split(','))
        where = '' if mv['status'] == '1' else f" and vod_id in('{id_list}')"
        return query.replace('where', f' where 1=1 {where} and ')


class VIPParse:
    @staticmethod
    def parse(url):
        parse_url = f"https://www.cuan.la/m3u8.php?url={url}"
        resp = requests.get(parse_url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'
        })
        if resp and resp.text:
            resp = resp.text
            token_index = resp.find('var bt_token = ') + len('var bt_token = ') + 1
            if token_index > 0:
                token_end_index = resp.find('"', token_index)
                token = resp[token_index: token_end_index]
                script_index = resp.find('var config = ') + len('var config= ')
                script_end_index = resp.find('lele.start()', script_index)
                script_config = resp[script_index: script_end_index]
                url_index = script_config.find('"url":') + len('"url":') + 1
                url_end_index = script_config.find('"', url_index)
                url = script_config[url_index: url_end_index]
                if token and len(token) == 16 and url:
                    from util.NeteaseUtil import NeteaseUtil
                    return NeteaseUtil.aes_decrypt_all('dvyYRQlnPRCMdQSe', token, url)
        return None


class LeDuoParse:
    @staticmethod
    def parse(vid):
        parse_url = f'https://api.leduotv.com/wp-api/glid.php?vid={vid}&isDp='
        resp = requests.get(parse_url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'
        })
        if resp and resp.content:
            resp = resp.content.decode('utf-8')
            if resp:
                url_flag = 'leduoplayer/index.php?url='
                script_index = resp.rfind('<script type="text/javascript">')
                start_index = resp.find(url_flag, script_index) + len(url_flag)
                end_index = resp.find('var u = navigator.userAgent;', start_index)
                mv_url = resp[start_index: end_index]
                if mv_url:
                    return mv_url.replace(' ', '').replace("'", '')\
                        .replace(';', '').replace('\r', '').replace('\n', '').replace('\t', '')
        return None


class Banner:

    def __init__(self):
        self.tops = []
        self.banner_url = 'https://v.qq.com'

    def parse_top(self, html):
        if html and isinstance(html, str):
            root = etree.HTML(html)
            name = root.xpath("//div[starts-with(@class,'site_slider ')]/div[2]//a/span/span/text()")
            img = root.xpath("//div[starts-with(@class,'site_slider ')]/div[2]//"
                             "a[not(contains(@data-bgimage,'common'))]/@data-bgimage")
            self.tops = [(n, img[i]) for (i, n) in enumerate(name)]

    def fetch_top(self):
        banner_list = []
        try:
            r = requests.get(self.banner_url, headers={'User-Agent': random.choice(Conf.UAS)})
            self.parse_top(r.content.decode('utf-8'))
            if self.tops and len(self.tops) > 0:
                YTV.pre_update_slide()
                for top in self.tops:
                    if top[0] != '大家在看':
                        tv_banner = dict()
                        tv_banner['id'] = str(uuid.uuid4())
                        tv_name = str(top[0])
                        tv_name = tv_name if '·' not in tv_name else tv_name[:tv_name.index('·')]
                        tv_banner['tv_name'] = tv_name
                        tv_banner['tv_img'] = top[1]
                        banner_list.append(tv_banner)
                        YTV.update_slide(tv_name, top[1])
            return banner_list
        except Exception as e:
            print(repr(e))


class Top:
    def __init__(self):
        self.index_url = 'https://v.qq.com/biu/ranks/?t=hotsearch'
        self.name_xpath = '//*[@id="app"]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/ol//li/a/span[2]/text()'

    def spider(self):
        r = requests.get(self.index_url, headers={'User-Agent': random.choice(Conf.UAS)})
        text = r.content.decode('utf-8')
        root = etree.HTML(text)
        return root.xpath(self.name_xpath)[:9]
