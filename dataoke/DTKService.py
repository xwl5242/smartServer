# -*- coding:utf-8 -*-
from config.DB import db
from dataoke.DTK import DtkOpenPlatform as dtk


class DTKService:

    @staticmethod
    def universal_parse(content):
        good_json = DTKService._send('TB_UNIVERSAL_PARSE', {'content': content})
        if good_json['code'] == 0:
            goods_id = good_json['data']['goodsId']
            if goods_id:
                return DTKService.privilege_link(goods_id)
            return None, "很抱歉没有找到商品"
        else:
            return None, good_json['msg']

    @staticmethod
    def privilege_link(goods_id):
        link = DTKService._send('PRIVILEGE_LINK', {'goodsId': goods_id})
        if link and link['code'] == 0 and link['data'] and link['data']['shortUrl']:
            return "0000", link['data']['shortUrl']
        return None, None

    @staticmethod
    def _send(api_key, args):
        url, method, version = DTKService._get_dtk_api(api_key)
        if url and method and version:
            params = {'version': version}
            params.update(args)
            return dtk.send(method, url, params)
        return None

    @staticmethod
    @db
    def _get_dtk_api(cursor, api_key):
        sql = f"select * from dtk_api where api_key='{api_key}' and del_flag='0'"
        cursor.execute(sql)
        api = cursor.fetchone()
        if api and api['api_req_url'] and api['api_req_method'] and api['api_version']:
            return api['api_req_url'], api['api_req_method'], api['api_version']
        return None, None, None


if __name__ == '__main__':
    pass

