# -*- coding:utf-8 -*-
import time
import uuid
import random
import requests
from lxml import etree
from config.DB import vip_db
from config.Config import Conf


class YTV:

    @staticmethod
    @vip_db
    def show_share_url(cursor):
        sql = "select switch_status ss from mac_setting where id=1"
        cursor.execute(sql)
        switch_status = cursor.fetchone()
        return switch_status['ss'] if switch_status else 0

    @staticmethod
    @vip_db
    def mac_setting(cursor):
        sql = "select play_switch playSwitch,ad_notice_switch adNoticeSwitch,ad_notice_content adNoticeContent " \
              "from mac_setting where id=1"
        cursor.execute(sql)
        mac_setting = cursor.fetchone()
        return mac_setting if mac_setting else None

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
        print(sql)
        cursor.execute(sql)
        total = cursor.fetchone()
        return total['total'] if total else 0

    @staticmethod
    @vip_db
    def get_soft_list(cursor, kw, page_no, page_size):
        page_no = int(page_no)
        page_size = int(page_size)
        kw_where = f" and (title like '%%{kw}%%') " if kw else ''
        sql = f"select * from soft where del_flag='0' {kw_where} order by create_time desc " \
              f"limit {page_no*page_size},{page_size}"
        cursor.execute(sql)
        count_sql = f"select count(1) total from soft where del_flag='0' {kw_where}"
        soft_list = cursor.fetchall()
        cursor.execute(count_sql)
        total = cursor.fetchone()['total']
        return soft_list, total

    @staticmethod
    def get_mv_type_list(mv_type, page_no, page_size):
        result = {}
        sub_types = Conf.mv_sub_type().get(mv_type)
        for sub_type in sub_types:
            mvs = YTV.get_mv_by_type(sub_type, page_no, page_size)
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
    def get_news(cursor):
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
              f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_serial from mac_vod " \
              f"where vod_status='1' and type_id not in (11, 21) order by vod_time_add desc limit 0,9"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_by_type(cursor, mv_type, page_no, page_size):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
             f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_serial from mac_vod " \
             f"where vod_status='1' and type_id={mv_type} and type_id not in (11, 21) order by vod_time_add desc " \
              f"limit {page_no * page_size},{page_size}"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_by_type_count(cursor, mv_type):
        sql = f"select count(1) total from mac_vod where vod_status='1' and type_id not in (11, 21) and type_id={mv_type}"
        cursor.execute(sql)
        total = cursor.fetchone()
        return total['total'] if total else 0

    @staticmethod
    @vip_db
    def get_mv_by_dy(cursor, page_no, page_size):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
              f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_serial from mac_vod " \
              f"where vod_status='1' and type_id not in (11, 21) and type_id between 6 and 12 order by vod_time_add desc " \
              f"limit {page_no * page_size},{page_size}"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_by_ds(cursor, page_no, page_size):
        page_no = int(page_no)
        page_size = int(page_size)
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
              f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_serial from mac_vod " \
              f"where vod_status='1' and type_id not in (11, 21) and type_id between 13 and 16 order by vod_time_add desc " \
              f"limit {page_no * page_size},{page_size}"
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    @vip_db
    def get_mv_detail(cursor, mv_id):
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
              f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_time_add," \
              f"vod_content,vod_play_note,vod_play_url,vod_serial from mac_vod where vod_status='1' and vod_id={mv_id}"
        cursor.execute(sql)
        return cursor.fetchone()

    @staticmethod
    @vip_db
    def get_mv_by_name(cursor, tv_name):
        sql = f"select vod_id,type_id,vod_name,vod_pic,vod_actor,vod_director,vod_blurb,vod_remarks," \
              f"vod_area,vod_lang,vod_year,vod_score,vod_score_all,vod_score_num,vod_time,vod_serial from mac_vod " \
              f"where vod_status='1' and type_id not in (11, 21) and vod_name like '%{tv_name}%' order by vod_time_add desc"
        cursor.execute(sql)
        return cursor.fetchall()


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
        return root.xpath(self.name_xpath)[:5]

