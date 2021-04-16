# -*- coding:utf-8 -*-
import json
import time
from tools.API import API
from tools.Music import Music
from tools.Smart import Smart
from tools.GirlMV import GirlMV
from tools.Gallery import Gallery
from wechat.WxService import WxService, WxMenuService
from flask import Flask, request, render_template, jsonify, send_file


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
            },
            {
                "type": "miniprogram",
                "name": "智慧助手",
                "url": "http://mp.weixin.qq.com",
                "appid": "wxc2a9b37969814f8a",
                "pagepath": "pages/index/index"
            }
        ]
    })
    return jsonify(ret)


##################
# 智能平台相关请求 #
##################
@app.route('/smart/menus')
def smart_menus():
    """
    菜单
    :return:
    """
    return jsonify(menus=API.menus())


@app.route('/smart/mv/girl')
def smart_mv_girl():
    """
    随机一个美女视频
    :return:
    """
    file_no, url = GirlMV().one()
    return jsonify(url=url, file_no=file_no)


@app.route('/smart/mv/girl/download/<file_no>')
def smart_mv_girl_download(file_no):
    import os
    path = os.path.join(os.path.dirname(__file__), 'tools', 'mv', f'{file_no}.mp4')
    return send_file(path)


@app.route('/smart/mv/parse')
def smart_mv_parse():
    """
    视频解析
    :return:
    """
    from tools.MVParse import MVParse
    if 'url' in request.args:
        v_url = request.args['url']
        v_type = request.args['type']
        v_type = v_type if v_type else 'jh'
        return MVParse(v_url).parse(v_type)
    return None, None


@app.route('/smart/music/search/<kw>')
def smart_music_search(kw):
    """
    音乐搜索服务
    :param kw: 音乐名称
    :return:
    """
    musics = Music.search(kw)
    return jsonify(musics=musics)


@app.route('/smart/music/download/<song_id>')
def smart_music_download(song_id):
    """
    音乐下载服务
    :param song_id: 音乐id
    :return:
    """
    return jsonify(download_url=Music.download(song_id))


@app.route('/smart/switch')
def smart_switch():
    """
    系统开关，控制功能开关
    :return:
    """
    return jsonify(switchs=Smart.switchs())


@app.route('/smart/switchs')
def smart_switchs():
    """
    系统开关，控制功能开关
    :return:
    """
    return jsonify(switchs=Smart.switchs())


@app.route('/smart/love')
def smart_love():
    """
    土味情话
    :return:
    """
    return API.love()


@app.route('/smart/garbage/<goods>')
def smart_garbage(goods):
    """
    垃圾分类
    :param goods: 垃圾名称
    :return:
    """
    return API.garbage(goods)


@app.route('/smart/short_url')
def smart_short_url():
    """
    短链接
    :return:
    """
    if 'url' in request.args:
        url = request.args['url']
        return API.short_url(url)
    return None


@app.route('/smart/article')
def smart_article():
    """
    每日一文
    :return:
    """
    return API.article()


@app.route('/smart/word')
def smart_word():
    """
    每日一言
    :return:
    """
    return API.word()


@app.route('/smart/xwlzhx20151118/gif/fetch')
def smart_gif_fetch():
    Gallery.gif_fetch()


@app.route('/smart/gif/<page_no>')
def smart_gif(page_no):
    """
    动态图
    :param page_no: 页码
    :return:
    """
    page_no = int(page_no) if page_no else 0
    return jsonify(gifs=Gallery.gif(page_no))


@app.route('/smart/wallpaper/type')
def smart_wallpaper_type():
    """
    精美壁纸类型
    :return:
    """
    wp_type = Gallery.wallpaper_type()
    wp_type = [wt for wt in wp_type if str(wt['id']) not in ['6', '30', '36']]
    return jsonify(wp_type=wp_type)


@app.route('/smart/wallpaper/list/<t>/<page_no>')
def smart_wallpaper_list(t, page_no):
    """
    分页获取精美壁纸
    :param t: 壁纸类型
    :param page_no: 页码
    :return:
    """
    return jsonify(wps=Gallery.wallpaper_list(t, page_no))


@app.route('/smart/suggest/save', methods=['POST'])
def smart_suggest_save():
    """
    留言功能
    :return:
    """
    tmp = request.json
    if tmp:
        Smart.suggest_save(tmp['suggest'])
    return jsonify(code=0)
    

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


