# -*- coding:utf-8 -*-
import time
import json
import hashlib
import requests


SIGN_METHOD = 'md5'


class TBK:

    def __init__(self):
        self.app_key = "32269578"
        self.app_secret = "08d416786ec87d7f8d4d4749701e6679"

    def md5(self, args):
        assert isinstance(args, dict), "args must be dict type"
        args['v'] = '2.0'
        args['format'] = 'json'
        args['app_key'] = self.app_key
        args['sign_method'] = SIGN_METHOD
        params = "&".join([f'{arg}={args.get(arg)}' for arg in args.keys()])
        _args = [f'{arg}{args.get(arg)}' for arg in args.keys()]
        _args.sort()
        _text = f'{self.app_secret}{"".join(_args)}{self.app_secret}'
        md5 = hashlib.md5()
        loc_bytes_utf8 = _text.encode(encoding="utf-8")
        md5.update(loc_bytes_utf8)
        sign = str(md5.hexdigest()).upper()
        return f'{params}&sign={sign}'

    def get_item(self, goods_id):
        params = {
            'platform': 2,
            'num_iids': goods_id,
            'method': 'taobao.tbk.item.info.get',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }
        req_url = f'http://gw.api.taobao.com/router/rest?{self.md5(params)}'
        resp = requests.get(req_url)
        resp = json.loads(resp.text)
        if resp and resp['tbk_item_info_get_response'] and resp['tbk_item_info_get_response']['results']:
            resp = resp['tbk_item_info_get_response']['results']
            if resp and resp['n_tbk_item'] and len(resp['n_tbk_item']) > 0:
                return resp['n_tbk_item'][0]
        return None


if __name__ == '__main__':
    print(TBK().get_item('634359353417'))




