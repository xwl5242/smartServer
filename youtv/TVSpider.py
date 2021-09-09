# -*- coding:utf-8 -*-
import json
import random
import requests
from config.DB import vip_db
from config.Config import Conf


class TVSpider:

    def __init__(self):
        self.__U = 'https://api.apibdzy.com/api.php/provide/vod/?ac=detail&pg='
        self.__T = {1: 1, 2: 2, 3: 3, 4: 4, 21: 6, 22: 7, 23: 8, 24: 9, 25: 10, 26: 6, 27: 12, 29: 11, 30: 19,
                    32: 13, 33: 14, 34: 15, 35: 16, 37: 3, 38: 3, 39: 3, 40: 3, 28: 4, 42: 4, 43: 4, 44: 4, 45: 4,
                    49: 4, 51: 4, 52: 4, 53: 4, 54: 4, 55: 4, 57: 20, 58: 14, 59: 15, 67: 4, 77: 4}

    def fetch(self, page_start, page_end):
        cur = 0
        try:
            exist_list = TVSpider.__exist()
            for pc in range(page_start, page_end+1):
                cur = pc
                print(cur)
                resp = requests.get(f'{self.__U}{pc}', headers={
                    'User-Agent': random.choice(Conf.UAS)
                })
                if resp and resp.text:
                    resp = json.loads(resp.text)
                    if resp and resp['code'] == 1:
                        for vod in resp['list']:
                            if int(vod['vod_id']) not in exist_list:
                                real_t = self.__T.get(int(vod['type_id']), "")
                                if real_t != "":
                                    vod['type_id'] = real_t
                                    TVSpider.__save(vod)
                # time.sleep(1)
        except:
            import traceback
            traceback.print_exc()
            print(cur)

    @staticmethod
    @vip_db
    def __exist(cursor):
        sql = "select vod_id from mac_vod_fanqie"
        cursor.execute(sql)
        exist_list = cursor.fetchall()
        return [int(e['vod_id']) for e in exist_list]

    @staticmethod
    @vip_db
    def __save(cursor, vod):
        sql = f"insert into mac_vod_fanqie values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
            f"%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
            f"%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cursor.execute(sql, args=(vod['vod_id'], vod['type_id'], vod['type_id_1'], vod['group_id'], vod['vod_name'],
                                      vod['vod_sub'], vod['vod_en'], vod['vod_status'], vod['vod_letter'],
                                      vod['vod_color'], vod['vod_tag'], vod['vod_class'], vod['vod_pic'],
                                      vod['vod_pic_thumb'], vod['vod_pic_slide'], vod['vod_actor'], vod['vod_director'],
                                      vod['vod_writer'], vod['vod_behind'], vod['vod_blurb'], vod['vod_remarks'],
                                      vod['vod_pubdate'], vod['vod_total'], vod['vod_serial'], vod['vod_tv'],
                                      vod['vod_weekday'], vod['vod_area'], vod['vod_lang'], vod['vod_year'],
                                      vod['vod_version'], vod['vod_state'], vod['vod_author'], vod['vod_jumpurl'],
                                      vod['vod_tpl'], vod['vod_tpl_play'], vod['vod_tpl_down'], vod['vod_isend'],
                                      vod['vod_lock'], vod['vod_level'], vod['vod_copyright'], vod['vod_points'],
                                      vod['vod_points_play'], vod['vod_points_down'], vod['vod_hits'],
                                      vod['vod_hits_day'], vod['vod_hits_week'], vod['vod_hits_month'],
                                      vod['vod_duration'], vod['vod_up'], vod['vod_down'], vod['vod_score'],
                                      vod['vod_score_all'], vod['vod_score_num'], vod['vod_time'], vod['vod_time_add'],
                                      vod['vod_time_hits'], vod['vod_time_make'], vod['vod_trysee'],
                                      vod['vod_douban_id'], vod['vod_douban_score'], vod['vod_reurl'],
                                      vod['vod_rel_vod'], vod['vod_rel_art'], vod['vod_pwd'], vod['vod_pwd_url'],
                                      vod['vod_pwd_play'], vod['vod_pwd_play_url'], vod['vod_pwd_down'],
                                      vod['vod_pwd_down_url'], vod['vod_content'], vod['vod_play_from'],
                                      vod['vod_play_server'], vod['vod_play_note'], vod['vod_play_url'].split('$$$')[1],
                                      vod['vod_down_from'], vod['vod_down_server'], vod['vod_down_note'],
                                      vod['vod_down_url'], vod['vod_plot'], vod['vod_plot_name'], vod['vod_plot_detail']))
        except:
            import traceback
            traceback.print_exc()
            print(sql)


if __name__ == '__main__':
    # 499 725
    # 2769
    TVSpider().fetch(1, 150)

