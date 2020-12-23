# -*- coding:utf-8 -*-
from config.DB import db
from dataoke.DTK import DtkOpenPlatform as dtk


class DTKService:

    @staticmethod
    def universal_parse(content):
        """
        淘系万能解析
        :param content:
        :return:
        """
        good_json = DTKService._send('TB_UNIVERSAL_PARSE', {'content': content})
        if good_json and good_json['code'] == 0:
            # {'commissionRate': 3.1, 'commissionType': 'COMMON', 'goodsId': '633240667694',
            # 'originInfo': {}, 'originType': '商品', 'originUrl': 'https://s.click.taobao.com/...'}
            return "0000", good_json['data']
        else:
            return None, good_json['msg']

    @staticmethod
    def tao_passwd_create(text, url):
        passwd_json = DTKService._send('TB_PASSWD_CREATE', {'text': text, 'url': url})
        if passwd_json and passwd_json['code'] == 0:
            # {'password_simple': '￥fkCpcJlsI6W￥', 'model': '10￥fkCpcJlsI6W￥/', 'longTpwd': '108.0￥fkCpcJlsI6W￥...'}
            return "0000", passwd_json['data']
        else:
            return None, passwd_json['msg']

    @staticmethod
    def goods_detail(goods_id):
        good_json = DTKService._send('GOODS_DETAIL', {'goodsId': goods_id})
        if good_json and good_json['code'] == 0:
            # {'id': -1, 'goodsId': '633240667694', 'title': '璞诱旗舰店...', 'dtitle': '璞诱旗..', 'originalPrice': 89.9,
            # 'actualPrice': 29.9, 'shopType': 1, 'goldSellers': -1, 'monthSales': 1005, 'twoHoursSales': -1,
            # 'dailySales': -1, 'commissionType': -1, 'desc': '', 'couponReceiveNum': 9256,
            # 'couponLink': 'https://uland.taobao.com/quan/..', 'couponEndTime': '2020-12-31 23:59:59',
            # 'couponStartTime': '2020-12-01 00:00:00', 'couponPrice': 60, 'couponConditions': '满89元减60元',
            # 'activityType': -1, 'createTime': '', 'mainPic': 'https://img.alicdn.com/...', 'marketingMainPic': '',
            # 'sellerId': '2208156096794', 'brandWenan': '', 'cid': -1, 'discounts': 1.0, 'commissionRate': 3.1,
            # 'couponTotalNum': 100000, 'haitao': -1, 'activityStartTime': '', 'activityEndTime': '',
            # 'shopName': '璞诱旗舰店', 'shopLevel': -1, 'descScore': 48378, 'brand': -1, 'brandId': -1, 'brandName': '',
            # 'hotPush': -1, 'teamName': '', 'itemLink': 'https://detail.tmall.com/...', 'tchaoshi': 1, 'dsrScore': -1,
            # 'dsrPercent': -1, 'shipScore': -1, 'shipPercent': -1, 'serviceScore': -1, 'servicePercent': -1,
            # 'imgs': 'https://img.alicdn.com/...,https://img.alicdn.com/...,https://img.alicdn.com/...,
            # https://img.alicdn.com/...', 'reimgs': '', 'quanMLink': 0, 'hzQuanOver': 0, 'yunfeixian': -1,
            # 'estimateAmount': 0, 'shopLogo': '', 'specialText': [], 'freeshipRemoteDistrict': 0, 'video': '',
            # 'detailPics': '', 'isSubdivision': 0, 'subdivisionId': 0, 'subdivisionName': '', 'subdivisionRank': 0,
            # 'directCommissionType': -1, 'directCommission': -1, 'directCommissionLink': '', 'tbcid': -1}
            return "0000", good_json['data']
        else:
            return None, good_json['msg']

    @staticmethod
    def privilege_link(goods_id):
        """
        高效转链
        :param goods_id:
        :return:
        """
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

