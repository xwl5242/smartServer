# -*- coding:utf-8 -*-
import os
import json
import base64
import requests
import threading
from tools.Utils import Utils
from urllib.parse import unquote
from tools.IPTV import HqTV, IpTV, HdTV, CCTV, WS_TV, GAT_TV, Service
from flask import Flask, jsonify, request, Response, render_template


M3U8 = os.path.join(os.path.dirname(__file__), 'm3u8')


def substr(string, start, end):
    start = start if start else 0
    end = end if (end or int(end) != 0) else len(string)
    return str(string)[start: end]


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(JSONEncoder, self).default(o)


app = Flask(__name__)
app.json_encoder = JSONEncoder
app.add_template_filter(substr, "substr")


@app.route('/xwlzhx20151118/video/sync')
def video_sync():
    HqTV().fetch()
    IpTV.fetch()
    HdTV.fetch()
    return jsonify({"result": "ok"})


@app.route('/iptv/config/<ver>')
def iptv_config(ver):
    return jsonify({"setting": Service.get_iptv_config(ver)})


@app.route('/iptv/video/channel')
def video_channel():
    return jsonify({'cctv': CCTV, 'ws_tv': WS_TV, 'gat_tv': GAT_TV})


@app.route('/iptv/video/by/name/<tv_name>')
def video_by_name(tv_name):
    return jsonify({'data': Service.get_video_by_tv_name(tv_name)})


@app.route('/iptv/video/player/<video_id>/<channel>')
def video_player(video_id, channel):
    video_id = str(video_id)
    channel = channel if channel else 1
    video_url = HqTV().get_video_url(video_id) if int(channel) == 1 else \
        (IpTV.get_video_url(video_id) if int(channel) == 2 else HdTV.get_video_url(video_id))
    return jsonify({"url": video_url})


@app.route('/iptv/player')
def player():
    return render_template("1.html")


@app.route('/iptv/m3u8')
def video_m3u8():
    # aHR0cCUzQSUyRiUyRjExMS40MC4xOTYuMjklMkZQTFRWJTJGODg4ODg4ODglMkYyMjQlMkYzMjIxMjI1NzY5JTJGaW5kZXgubTN1OA==
    url = request.args['m3u8']
    if url:
        url = unquote(base64.b64decode(url).decode("utf-8"))
        resp = requests.get(url, headers=Utils.ua())
        if resp and resp.text:
            url_list = [u.replace("\r", "") for u in resp.text.split('\n') if 'hls.ts' in u]
            threading.Thread(target=ts_download, args=(url_list,))
        if resp and resp.content:
            resp = Response(resp.content, content_type='application/x-mpegURL')
            return resp
    return None


@app.before_request
def video_hls_ts():
    if '.ts' in request.path:
        url = request.path
        url = url[url.rfind('/'):]
#         http://111.40.196.29/PLTV/88888888/224/3221225769/
        resp = requests.get('http://111.40.196.29/PLTV/88888888/224/3221225769'+url, headers=Utils.ua())
        if resp and resp.content:
            resp = Response(resp.content, content_type='application/x-mpegURL')
            return resp
        # return redirect('http://111.40.196.29/PLTV/88888888/224/3221225769'+url)


def ts_download(url_list):
    for url in url_list:
        b64_url = base64.b64encode(url).decode("utf-8")
        resp = requests.get(url, headers=Utils.ua())
        if resp and resp.content:
            with open(os.path.join(M3U8, b64_url), 'wb') as f:
                f.write(resp.content)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)


