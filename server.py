# -*- coding:utf-8 -*-
import json
from wechat.MsgReply import MsgReply
from wechat.WxService import WxService
from flask import Flask, request, render_template, jsonify


app = Flask(__name__)


@app.route("/wx/search/ret", methods=['GET'])
def wx_search_ret():
    wx_id = request.args['wx_id']
    msg_id = request.args['msg_id']
    smart_ret = WxService.query_smart_search(wx_id, msg_id)
    return render_template('search.html', smart_ret=smart_ret)


@app.route("/wx_msg.html", methods=['GET', 'POST'])
def wx_msg():
    """
    微信消息服务器，接受消息|事件，被动回复消息，加密方式传输
    :return:
    """
    # noinspection PyBroadException
    try:
        post_xml_msg = request.get_data(as_text=True)
        if request.method == 'GET':
            return request.args['echostr']
        else:
            nonce = request.args['nonce']
            time_stamp = request.args['timestamp']
            msg_signature = request.args['msg_signature']
            return MsgReply.reply(post_xml_msg, msg_signature, time_stamp, nonce, True)
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)


