# -*- coding:utf-8 -*-
import uuid
import requests
import threading
# from config.DB import db
from config.Config import Conf
from wechatpy import parse_message
from wechat.WxService import WxService
from wechat.MsgCrypt import WXBizMsgCrypt
from dataoke.DTKService import DTKService
from wechatpy.replies import ArticlesReply, TextReply


class MsgReply:

    @staticmethod
    def go_search(wx_id, wx_key_word, wx_msg_id):
        """
        关键字搜索功能
        :param wx_id: 消息发送者
        :param wx_key_word: 关键字信息
        :param wx_msg_id: 消息唯一id
        :return:
        """
        import time, json
        save_time = time.time()
        tv = requests.get('https://api.quandidi.top/vip/search/'+wx_key_word)
        if tv and tv.status_code == 200:
            tv = tv if tv else None
            tv = json.loads(tv.content.decode('utf-8'))
            if len(tv['mvs']) > 0:
                tv = f"http://xwlzhx20151118.quanchonger.com/index.php/" \
                    f"vod/search.html?wd={requests.utils.quote(wx_key_word)}"
                WxService.save_smart_search(wx_id, wx_key_word, '0', save_time, wx_msg_id, tv)
        good_info = DTKService.universal_parse(wx_key_word)
        if good_info:
            good_id = good_info['goodsId']
            if good_id:
                short_url = DTKService.privilege_link(good_id)
                if short_url:
                    WxService.save_smart_search(wx_id, wx_key_word, '1', save_time, wx_msg_id, good_id+"@"+short_url)

    @staticmethod
    def reply(post_xml_msg, s_msg_signature, s_time_stamp, s_nonce, is_crypt=False):
        """
        回复消息
        :param post_xml_msg: wx服务器发送过来的post数据
        :param s_msg_signature: 签名
        :param s_time_stamp: 时间戳
        :param s_nonce: nonce字符串
        :param is_crypt: 是否安全加密传输消息
        :return:
        """
        crypt = {}
        if is_crypt:
            crypt = WXBizMsgCrypt(Conf.WX_MSG_TOKEN, Conf.WX_MSG_AES_KEY, Conf.WX_APP_ID)
            ret, xml = crypt.decrypt_msg(post_xml_msg, s_msg_signature, s_time_stamp, s_nonce)
        else:
            ret, xml = 0, post_xml_msg
        reply = {}
        if 0 == ret:
            msg = parse_message(xml)
            if 'text' == msg.type:
                msg_id = str(uuid.uuid4())
                go_search_thread = threading.Thread(target=MsgReply.go_search,
                                                    args=(msg.source, msg.content, msg_id,))
                go_search_thread.start()
                reply = ArticlesReply()
                reply.source = msg.target
                reply.target = msg.source
                reply.add_article({
                    'title': u'快点我查看详情',
                    'description': u'客官，已经为您生成专属结果，快前往查看吧！',
                    'url': 'http://smart.quanchonger.com/wx/search/ret?wx_id='+msg.source+'&msg_id='+msg_id,
                    'image': 'https://www.quanchonger.com/msg_banner.png'
                })
            if 'event' == msg.type:
                reply = TextReply()
                reply.source = msg.target
                reply.target = msg.source
                if 'subscribe' == msg.event:
                    # 用户关注
                    reply.content = """终于等到你，欢迎您的关注!
这里是您的智慧生活助手，在这里你将会体会到丰富有趣的科技交互！
1. 公众号回复任意影视剧集名称关键字，即可快速搜索影视内容
2. 公众号回复任意单个且完整的淘口令，即可快速搜索优惠内容
3. 公众号会不间断更新其他丰富有趣的科技生活助手，敬请期待
                    """
        else:
            pass
        if is_crypt:
            ret, s_xml = crypt.encrypt_msg(reply.render(), s_nonce)
            return str(s_xml)
        else:
            return reply.render()


