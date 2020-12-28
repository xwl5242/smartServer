# -*- coding:utf-8 -*-
import json
from wechat.MsgReply import MsgReply
from dataoke.DTKService import DTKService
from wechat.WxService import WxService, WxMenuService
from flask import Flask, request, render_template, jsonify


def substr(string, start, end):
    start = start if start else 0
    end = end if (end or int(end) != 0) else len(string)
    return str(string)[start: end]


app = Flask(__name__)
app.add_template_filter(substr, "substr")


@app.route("/wx/taobao.html", methods=['GET'])
def wx_taobao():
    wx_msg_ret = request.args['wx_msg_ret']
    if wx_msg_ret:
        rets = str(wx_msg_ret).split("@")
        ret, goods_detail = DTKService.goods_detail(rets[0])
    return render_template('taobao.html', shortUrl=rets[1], goods_detail=goods_detail)


@app.route("/wx/taobao/detail.html", methods=['GET'])
def wx_taobao_detail():
    goods_id = request.args['goodsId']
    ret, goods_detail = DTKService.goods_detail(goods_id)
    if ret == "0000" and goods_detail:
        ret0, pwd = DTKService.tao_passwd_create(goods_detail['dtitle'], goods_detail['couponLink'])
        return render_template('tbdetail.html', detail=goods_detail, pwd=pwd['password_simple'])
    return render_template('404.html')


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


@app.route("/wx_create_menu.html", methods=['GET', 'POST'])
def wx_create_menu():
    ret = WxMenuService().create({
        "button": [
            {
                "type": "view",
                "name": "优惠商城",
                "url": "https://www.quanchonger.com"
            },
            {
                "type": "miniprogram",
                "name": "小汪影视",
                "url": "http://mp.weixin.qq.com",
                "appid": "wx1f5d6afca3c44aab",
                "pagepath": "pages/index/index"
            }
        ]
    })
    return jsonify(json.loads(ret))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)


