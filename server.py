# -*- coding:utf-8 -*-
import json
import time
from tools.Chp import CHP
from youtv.YouTV import YTV
from tools.Music import Music
from tools.Smart import Smart
from tools.Gallery import Gallery
from wechat.WxService import WxService, WxMenuService
from flask import Flask, request, render_template, jsonify


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


######################
# 微信智能回复相关请求 #
######################
@app.route('/reply/msg.html', methods=['GET', 'POST'])
def reply_msg():
    """
    微信消息服务器，接受消息|事件，被动回复消息，加密方式传输
    :return:
    """
    # noinspection PyBroadException
    try:
        from wechat.MsgReply import MsgReply
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


@app.route('/reply/result.html', methods=['GET'])
def reply_result():
    """
    微信搜索结果页面
    :return:
    """
    wx_id = request.args['wx_id']
    msg_id = request.args['msg_id']
    smart_ret = WxService.query_smart_search(wx_id, msg_id)
    if smart_ret:
        return render_template('reply/result.html', smart_ret=smart_ret)
    return render_template('reply/404.html', flag='no-result')


@app.route('/reply/tb.html', methods=['GET'])
def reply_tb():
    """
    优惠券搜索结果页面
    :return:
    """
    from taoke.DTK import DTKService
    wx_msg_ret = request.args['wx_msg_ret']
    if wx_msg_ret:
        ret_list = str(wx_msg_ret).split("@")
        # 获取淘宝商品详情
        goods_detail = DTKService.goods_detail(ret_list[0])
        if goods_detail and goods_detail['couponLink']:
            return render_template('reply/tb.html', shortUrl=ret_list[1], goods=goods_detail)
    return render_template('reply/404.html', flag='no-coupon')


@app.route('/reply/tb_detail.html', methods=['GET'])
def reply_tb_detail():
    """
    优惠券详情页面
    :return:
    """
    from taoke.DTK import DTKService
    goods_id = request.args['goodsId']
    # 查询商品详情
    goods_detail = DTKService.goods_detail(goods_id)
    if goods_detail and goods_detail['dtitle'] and goods_detail['couponLink']:
        # 创建自己的淘口令
        pwd = DTKService.tao_twd_create(goods_detail['dtitle'], goods_detail['couponLink'])
        return render_template('reply/tb_detail.html', detail=goods_detail, pwd=pwd['password_simple'])
    return render_template('reply/404.html', flag='no-coupon')


@app.route('/reply/404/<flag>', methods=['GET'])
def reply_404(flag):
    return render_template('reply/404.html', flag=flag)


@app.route('/wx_create_menu.html', methods=['GET', 'POST'])
def wx_create_menu():
    """
    微信创建自定义菜单
    :return:
    """
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


@app.route('/wx_update_menu.html', methods=['GET', 'POST'])
def wx_update_menu():
    """
    微信更新自定义菜单
    :return:
    """
    ret = WxMenuService().update({
        "button": [
            {
                "type": "view",
                "name": "优惠商城",
                "url": "https://www.quanchonger.com"
            },
            # {
            #     "type": "view",
            #     "name": "小汪影视",
            #     "url": "http://xwlzhx20151118.quanchonger.com"
            # }
            {
                "type": "miniprogram",
                "name": "小汪影视",
                "url": "http://mp.weixin.qq.com",
                "appid": "wx1f5d6afca3c44aab",
                "pagepath": "pages/index/index"
            }

        ]
    })
    return jsonify(ret)


##################
# 智能平台相关请求 #
##################
@app.route('/smart/dy/parse')
def smart_dy_parse():
    """
    抖音视频解析
    :return:
    """
    from tools.DY import DouYin
    if 'url' in request.args and 'douyin.com' in request.args['url']:
        v_url = request.args['url']
        file_id = DouYin.parse(v_url)
    else:
        file_id = None
    return jsonify({"file_id": file_id})


@app.route('/smart/music/search/<kw>')
def smart_music_search(kw):
    musics = Music.search(kw)
    return jsonify(musics=musics)


@app.route('/smart/music/download/<song_id>')
def smart_music_download(song_id):
    return jsonify(download_url=Music.download(song_id))


@app.route('/smart/chp')
def smart_chp():
    return CHP.chp()


@app.route('/smart/gif/<page_no>')
def smart_gif(page_no):
    page_no = int(page_no) if page_no else 0
    return jsonify(gifs=Gallery.gif(page_no))


@app.route('/smart/wallpaper/type')
def smart_wallpaper_type():
    return jsonify(wp_type=Gallery.wallpaper_type())


@app.route('/smart/wallpaper/list/<t>/<page_no>')
def smart_wallpaper_list(t, page_no):
    return jsonify(wps=Gallery.wallpaper_list(t, page_no))


@app.route('/smart/suggest/save', methods=['POST'])
def smart_suggest_save():
    tmp = request.json
    if tmp:
        Smart.suggest_save(tmp['suggest'])
    return jsonify(code=0)


####################
# 莜视频平台相关请求 #
####################
top_list = {'l': [], 'e': None}
# 页面顶部轮播banner
banner_list = {'l': [], 'e': None}


@app.route('/vip/index')
def index():
    """
    首页
    :return:
    """
    news = YTV.get_news()
    dys = YTV.get_mv_by_dy(2, 9)
    dss = YTV.get_mv_by_ds(2, 9)
    zys = YTV.get_mv_by_type(3, 2, 9)
    dms = YTV.get_mv_by_type(4, 2, 9)
    mvs = {'dys': dys, 'dss': dss, 'zys': zys, 'dms': dms}
    total = YTV.get_vod_total()
    today = YTV.get_vod_update()
    return jsonify(news=news, mvs=mvs, total=total, today=today)


@app.route('/vip/mvtypes')
def mvtypes():
    mv_types = YTV.get_mv_type()
    return jsonify(mv_types=mv_types)


@app.route('/vip/mv/type/<mv_type>/<pageno>')
def mv_type_pageno(mv_type, pageno):
    mvs = YTV.get_mv_type_list(mv_type, pageno, 9)
    return jsonify(mvs=mvs)


@app.route('/vip/mv/subtype/<mv_subtype>/<pageno>')
def mv_subtype_pageno(mv_subtype, pageno):
    mvs = YTV.get_mv_by_type(mv_subtype, pageno, 9)
    total = YTV.get_mv_by_type_count(mv_subtype)
    return jsonify(mvs=mvs, total=total)


@app.route('/vip/search/<tv_name>')
def search(tv_name):
    """
    根据视频名称搜索资源
    :param tv_name: 视频名称
    :return: 视频mv list
    """
    return jsonify(mvs=YTV.get_mv_by_name(tv_name))


@app.route('/vip/detail/<tv_id>')
def detail(tv_id):
    """
    根据视频id获取视频详情信息
    :param tv_id: 视频id
    :return: 视频详情信息
    """
    return jsonify(mv=YTV.get_mv_detail(tv_id))


@app.route('/vip/switch_status')
def switch_status():
    return jsonify(status=YTV.show_share_url())


@app.route('/vip/mac_setting')
def mac_setting():
    return jsonify(mac_setting=YTV.mac_setting())


@app.route('/vip/banner')
def banner():
    """
    首页顶部轮播图  来自腾讯视频  每2个小时更新
    :return: banner list
    """
    from youtv.YouTV import Banner
    tp = Banner()
    expire = banner_list.get('e', None)
    now = int(time.time() * 1000)
    if expire and (now < expire - 60 * 1000):
        pass
    else:
        banner_list['e'] = int(now + 7200000)
        banner_list['l'] = tp.fetch_top()
    return jsonify(banner_list=banner_list['l'])
    # return jsonify(banner_list=[])


@app.route('/vip/top')
def top():
    """
    百度搜索风云榜 每2个小时更新
    :return: top list
    """
    from youtv.YouTV import Top
    top = Top()
    expire = top_list.get('e', None)
    now = int(time.time() * 1000)
    if expire and (now < expire - 60 * 1000):
        pass
    else:
        top_list['e'] = now + 7200 * 1000
        top_list['l'] = top.spider()
    return jsonify(top_list=top_list['l'])
    

#################
# 券宠儿相关请求 #
#################
@app.route('/quanchonger/update')
def quanchonger_update():
    import requests
    pc_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    wap_header = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    }
    pc_resp = requests.get('http://www.quanchonger.com/index.php', headers=pc_header)
    time.sleep(1)
    wap_resp = requests.get('http://www.quanchonger.com/index.php', headers=wap_header)
    pc = pc_resp.content.decode('utf-8')
    pc = pc[pc.index('<!DOCTYPE html>'):]
    pc = pc[:-5]
    pc = pc.replace("友情链接#LINK#", f"友情链接 | {YTV.get_quanchonger_link_html()}")
    pc = pc.replace("'); })();", "")
    with open('/usr/src/app/quanchonger/index.html', 'w') as pcw:
        pcw.write(pc)
    wap = wap_resp.content.decode('utf-8')
    wap = wap[wap.index('<!DOCTYPE html>'):]
    wap = wap[:-5]
    group_index = wap.find('<div class="top-line-group')
    if group_index and group_index > 0:
        end_index = wap.find('</div>', group_index)
        if end_index and end_index > 0:
            pre = wap[0:end_index + 6]
            sub = wap[end_index + 6:]
            app_download = '<div class="top-line-group show_module">' \
                           '<div class="top-line" style="justify-content: center;font-size:12px;">' \
                           '<a href="http://quanchonger.com/quanchonger.html" style="color:red;">' \
                           '点击前往下载手机APP</a></div></div>'
            wap = pre + app_download + sub
    with open('/usr/src/app/quanchonger/h5.html', 'w') as h5w:
        h5w.write(wap)
    return jsonify(pc=len(pc), wap=len(wap))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)


