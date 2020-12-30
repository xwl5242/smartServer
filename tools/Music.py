# -*- coding:utf-8 -*-
import json
import requests
from util.NeteaseUtil import NeteaseUtil as bu


class NeteaseMusic:

    """
    网易云音乐功能
    """
    aes_key = '0CoJUm6Qyw8W8jud'
    secret = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a' \
             '876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6' \
             'c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546' \
             'b8e289dc6935b3ece0462db0a22b8e7'
    search_url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
    search_post_data = '{"hlpretag":"<span class=\\"s-fc7\\">","hlposttag":"</span>","s":"@song@",' \
                       '"type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}'
    download_url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
    download_post_data = '{"ids":"[#SONGID#]","level":"standard","encodeType":"aac","csrf_token":""}'

    @classmethod
    def music_list(cls, song):
        """
        根据歌曲名称关键字获取歌曲id
        :param song:
        :return: song_name,singer,pic_url,target_url
        """
        music_list = []
        try:
            encrypt_en = bu.aes_encrypt(cls.aes_key, cls.search_post_data.replace('@song@', song))
            aes_key = bu.get_random_key(16)
            params = bu.aes_encrypt(aes_key, encrypt_en)
            enc_sec_key = bu.rsa_encrypt(aes_key, '010001', cls.secret)
            resp = requests.post(cls.search_url, headers=bu.rand_ua(),
                                 data={'params': params, 'encSecKey': enc_sec_key})
            resp = json.loads(resp.text)
            if resp['result'] and len(resp['result']['songs']) > 0:
                resp = resp['result']['songs']
                for _song in resp:
                    song_id = _song['id']
                    song_name = _song['name']
                    singer, fm_url = "", ""
                    if _song['ar'] and len(_song['ar']) > 0:
                        singer = _song['ar'][0]['name']
                    if _song['al']:
                        fm_url = _song['al']['picUrl']
                    music_list.append({'song_name': song_name, 'singer': singer,
                                       'fm_url': fm_url, 'url': f"http://music.163.com/song/{song_id}"})
            return music_list
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def download(cls, song_id):
        """
        根据歌曲id获取歌曲的下载地址
        :param song_id: 歌曲id
        :return: 歌曲下载地址，歌曲大小
        """
        try:
            song_id = str(song_id)
            encrypt_en = bu.aes_encrypt(cls.aes_key, cls.download_post_data.replace('#SONGID#', song_id))
            aes_key = bu.get_random_key(16)
            params = bu.aes_encrypt(aes_key, encrypt_en)
            enc_sec_key = bu.rsa_encrypt(aes_key, '010001', cls.secret)
            resp = requests.post(cls.download_url, headers=bu.rand_ua(),
                                 data={'params': params, 'encSecKey': enc_sec_key})
            if resp.status_code == 200 and resp and resp.text:
                resp = json.loads(resp.text)
                if resp['data'] and len(resp['data']) and resp['code'] == 200:
                    resp = resp['data'][0]
                    return resp['url']
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None


class QQMusic:

    @staticmethod
    def music_list(song_name):
        music_list = []
        sip = ['http://ws.stream.qqmusic.qq.com/', 'http://isure.stream.qqmusic.qq.com/']
        try:
            song_search_url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&n=2&w={song_name}&format=json"
            song_search_ret = requests.get(song_search_url)
            song_search_ret = json.loads(song_search_ret.text)
            if song_search_ret['code'] == 0:
                song_list = song_search_ret['data']['song']['list']
                for song in song_list:
                    songmid = song['songmid']
                    albummid = song['albummid']
                    song_name = song['songname']
                    singer = song['singer'][0]['name'] if song['singer'] and len(song['singer']) > 0 else ''
                    fm_url = f"http://y.gtimg.cn/music/photo_new/T002R180x180M000{albummid}.jpg"
                    music_list.append({'song_name': song_name, 'signer': singer, 'songmid': songmid,
                                       'fm_url': fm_url, 'url': f'http://y.qq.com/#type=song&id={song.get("songid")}'})
            return music_list
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def download(songmid):
        play_prev_url = f"https://u.y.qq.com/cgi-bin/musicu.fcg?format=json&data=" \
            f"%7B%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22" \
            f"method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%22358840384%22%2C%22" \
            f"songmid%22%3A%5B%22{songmid}%22%5D%2C%22" \
            f"songtype%22%3A%5B0%5D%2C%22uin%22%3A%221443481947%22%2C%22" \
            f"loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22" \
            f"comm%22%3A%7B%22uin%22%3A%2218585073516%22%2C%22format%22%3A%22" \
            f"json%22%2C%22ct%22%3A24%2C%22cv%22%3A0%7D%7D"
        play_ret = requests.get(play_prev_url)
        play_ret = json.loads(play_ret.text)
        if play_ret['code'] == 0 and play_ret['req_0']['code'] == 0:
            play_data = play_ret['req_0']['data']['midurlinfo']
            if len(play_data) > 0:
                return play_data[0]['purl']
        return None


class Music:

    @staticmethod
    def search(song_name):
        music_list = []
        music_list.extend(QQMusic.music_list(song_name))
        music_list.extend(NeteaseMusic.music_list(song_name))
        return [music for music in music_list if music['url']]


if __name__ == '__main__':
    # print(NeteaseMusic.music_list('无期'))
    # print(NeteaseMusic.download('1374154676'))
    # print(QQMusic.music_list('无期'))
    print(Music.search('无期'))
    # print(len(Music.search('无期')))



