# -*- coding:utf-8 -*-
import json
from flask import Flask, jsonify
from tools.IPTV import HqTV, IpTV, HdTV, CCTV, WS_TV, GAT_TV


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
    HqTV.fetch()
    # IpTV.fetch()
    # HdTV.fetch()
    return jsonify({"result": "ok"})


@app.route('/video/channel')
def video_channel():
    return jsonify({'cctv': CCTV, 'ws_tv': WS_TV, 'gat_tv': GAT_TV})


@app.route('/video/by/name/<tv_name>')
def video_by_name(tv_name):
    return jsonify({'data': IpTV.get_video_by_name(tv_name)})


@app.route('/video/player/<video_id>/<channel>')
def video_player(video_id, channel):
    video_id = str(video_id)
    channel = channel if channel else 1
    video_url = HqTV.get_video_url(video_id) if int(channel) == 1 else \
        (IpTV.get_video_url(video_id) if int(channel) == 2 else HdTV.get_video_url(video_id))
    return jsonify({"url": video_url})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)


