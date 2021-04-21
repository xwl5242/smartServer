# -*- coding:utf-8 -*-
import os
import json
import time
from tools.API import API
from tools.Music import Music
from tools.Smart import Smart
from tools.GirlMV import GirlMV
from tools.Gallery import Gallery
from util.NeteaseUtil import NeteaseUtil
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
    if 'ver' in request.args:
        ver = request.args['ver']
        return jsonify(menus=API.menus_ver(ver))
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
        file_no, url = MVParse(v_url).parse(v_type)
        return jsonify(file_no=file_no, url=url)
    return jsonify(file_no=None, url=None)


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


@app.route('/smart/switch/<ver>')
def smart_switch_ver(ver):
    """
    系统开关，根据版本查询对应的控制开关
    :param ver:
    :return:
    """
    return jsonify(switchs=Smart.switch_ver(ver))


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
    article, file_no = API.article()
    return jsonify(article=article, file_no=file_no)


@app.route('/smart/article/download/<file_no>')
def smart_article_download(file_no):
    """
    每日一文下载
    :return:
    """
    import os
    return send_file(os.path.join(os.path.dirname(__file__), 'tools', 'mv', f'{file_no}.txt'))


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


@app.route('/smart/xwlzhx20151118/tools/mv/clear')
def tools_mv_clear():
    """
    清空tools/mv
    :return:
    """
    path = os.path.join(os.path.dirname(__file__), 'tools', 'mv')
    for p in os.listdir(path):
        os.remove(os.path.join(path, p))
    return 'ok!'


@app.route('/smart/wallpaper/list/<t>/<page_no>')
def smart_wallpaper_list(t, page_no):
    """
    分页获取精美壁纸
    :param t: 壁纸类型
    :param page_no: 页码
    :return:
    """
    return jsonify(wps=Gallery.wallpaper_list(t, page_no))


@app.route('/smart/wallpaper/download')
def smart_wallpaper_download():
    if 'url' in request.args:
        return Gallery.wallpaper_download(request.args['url'])
    return None


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


PROXY_SERVER_CONFIG = 'Xr2eprEZhsfMmdBZ3t1VGm1sCNrPTupaUS31gXut/RyXNu0itNuqzztRXtZ+ahOimiupARcH8xwdvQdGQT' \
                      'Qt3SNpCM2QJctaWs3y+AnW4JXkhf1Rt/jHvS4Gd52On5ikjjVRaLW/aVjcS3USO/WFuIoClgwiMaHWdY44' \
                      'eVyJCVs0MiJlHF3wfKvGH2ioUnGIZkPv3QjsB7xESZ5VZ6OzfKOZf/xQ5z/KkK2J6X3XyLhrgWuoxLPPAr' \
                      'sFMLNCUwXkSmuQnKkfny2H/v1Aq10YKiGt7VO4iT2rzqSawjLOYA0GnrxLFKobImJR0f0XUf7SBokt5dMO' \
                      'gqae4kt7bFs0KcjuaA10zjfQLtG8AAPu3Hkg33bqDFfs8kq0+Px8vX19jgymSX2PYn/BefVNdHE/fuvxCL' \
                      'cniwfL2IPqI4ab81jbjNRUgmaokzDy45c6aAFgopE3RSgpxNJSBAwKRgWXiOgqcWZEI+eVHHtXAEO/cSlZ' \
                      '9mkCM6MDc8R0aOvdeM234syf/E9wRgxwJYJzFhhX/jyJYDFK2mqW4yko67o/d50jdFfC1mUShssW3xDr+F' \
                      'uxjhj70fD7a9pkS6DY8aPA0XOgVVwHbjDHQ8P4kzHQa+my+3qhKHOrpu/gwsREa2IAMdsUM5ig8+fbrKXD' \
                      '+bI+02WnSZzPG9030tImxrXAM4/zy0fXGT2LHT6MTbJWz1sPyaGHk/wTjISGRpuw595RZjVrOZh1h14hd6' \
                      'dm7KdcnUeZsf4uUnVGr4kPhSRCCuLyp1PnWrer8/Gg6iUpVU/BcdRBaNDR3JeM4ISP8pgemrNahGBN6pUw' \
                      'nQie28x048IJVYrHSEZnpWnt7Cc2VaTLF1DIpD//63eWhywI8Q0AhIsDgbmtWrt6wrqGkk31tNBE0kT2Z1' \
                      'JkhFwLZk/JKbPkQhdZtnCmaLA+ihAxtUxwI6EwvcS9krNWm7nnxjv+vWbiA6Y3hLTfDKvN6O/cF6P7z5E2' \
                      '7pqGSB0SBmRkF/9qekqodf/fKD7CDnLRHMlR7W4sU5233w5HM8ihep7HYCqLjxKkqZUpLXNyN+e27mYquc' \
                      'WrRb9IVhu760VTXUCn161y'


@app.route('/smart/xwlzhx20151118/tiktok/version')
def smart_tiktok_version():
    ver_path = os.path.join(os.path.dirname(__file__), 'tools', 'tiktok.ver')
    with open(ver_path, 'r') as f:
        return jsonify(vers=str(f.read()).split(','))
    return []


@app.route('/smart/xwlzhx20151118/proxy/server/url/list')
def smart_proxy_server_url_list():
    return jsonify(urls=['加拿大', '加拿大1', '美国', '美国东部', '美国西部', '法国', '德国', '日本',
                         '东京', '新加坡', '英国', '英国1', '荷兰', '香港', '密克罗尼西亚1', '密克罗尼西亚2'])


@app.route('/smart/xwlzhx20151118/proxy/server/pac')
def smart_proxy_server_pac():
    if 'u' in request.args:
        config = json.loads(NeteaseUtil.aes_decrypt('xwlzhx2015111821', PROXY_SERVER_CONFIG))
        return "var FindProxyForURL = function(url, host){var blackList = new Array('192.168.*','127.0.0.1'," \
               "'134.209.63.251','astarvpn.center','*.douyu.com','154.17.5.226','51.79.17.3','154.17.5.226'," \
               "'51.83.141.81','51.178.130.187','51.89.192.130','51.195.5.186','51.81.93.81','51.89.233.86','51.79.21.9'," \
               "'51.75.54.187','64.227.111.121','51.91.128.35','51.89.20.176','206.189.143.159','149.28.221.137'," \
               "'51.81.245.164','128.199.171.254','64.227.75.168','172.105.162.185','*.alipay.com','*.alipayobjects.com'," \
               "'*.alicdn.com','*.payssion.com','*.95516.com','154.17.19.107','167.99.92.16','172.104.97.56','66.42.42.141'," \
               "'194.169.181.190','156.146.35.139','159.89.0.33','23.224.68.58','165.227.42.38','154.17.4.126'," \
               "'51.89.20.176	','135.125.190.230	','154.17.9.217','172.105.173.146','89.187.160.187','mapi.yuansfer.com'," \
               "'154.17.3.3','154.17.6.239');for(var i = 0;i < blackList.length;i++){if(shExpMatch(host,blackList[i]))" \
               "return 'DIRECT';} return 'HTTPS " + str(config.get(request.args['u'])) + "';}"
    return None
    

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


