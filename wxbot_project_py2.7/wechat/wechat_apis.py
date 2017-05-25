#!/usr/bin/env python
# coding: utf-8

#===================================================
from utils import *
from config import Constant
from config import Log
#---------------------------------------------------
import sys
import os
import cookielib
import random
import requests
import time
import xml.dom.minidom
# for media upload
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder
#===================================================


class WXAPI(object):

    def __init__(self, host):
        self.wx_host = host
        self.wx_filehost = ''
        self.wx_conf = {}
        # jsLogin时这个appid只能使用: wx782c26e4c19acffb
        self.appid = Constant.API_APPID
        self.uuid = ''
        self.redirect_uri = ''
        self.skey = ''
        self.sid = ''
        self.uin = ''
        self.pass_ticket = ''
        self.base_request = {}
        self.synckey_dic = {}
        self.synckey = ''
        self.device_id = 'e' + repr(random.random())[2:17]
        # device_id: 登录手机设备
        # web wechat 的格式为: e123456789012345 (e+15位随机数)
        # mobile wechat 的格式为: A1234567890abcde (A+15位随机数字或字母)
        self.user_agent = Constant.API_USER_AGENT
        self.cookie = None

        self.conf_factory()

        self.User = []  # 登陆账号信息
        self.MemberList = []  # 好友+群聊+公众号+特殊账号
        self.MemberCount = 0
        self.ContactList = []  # 好友
        self.GroupList = []  # 群
        self.GroupMemeberList = {}  # 群聊成员字典
                                    # "group_id": [
                                    #       {member}, ...
                                    # ]
        self.PublicUsersList = []  # 公众号／服务号
        self.SpecialUsersList = []  # 特殊账号

        self.media_count = 0

    def conf_factory(self):
        e = self.wx_host  # wx.qq.com
        t, o, n = "login.weixin.qq.com", "file.wx.qq.com", "webpush.weixin.qq.com"

        if e.find("wx2.qq.com") > -1:
            t, o, n = "login.wx2.qq.com", "file.wx2.qq.com", "webpush.wx2.qq.com"
        elif e.find("wx8.qq.com") > -1:
            t, o, n = "login.wx8.qq.com", "file.wx8.qq.com", "webpush.wx8.qq.com"
        elif e.find("qq.com") > -1:
            t, o, n = "login.wx.qq.com", "file.wx.qq.com", "webpush.wx.qq.com"
        elif e.find("web2.wechat.com") > -1:
            t, o, n = "login.web2.wechat.com", "file.web2.wechat.com", "webpush.web2.wechat.com"
        elif e.find("wechat.com") > -1:
            t, o, n = "login.web.wechat.com", "file.web.wechat.com", "webpush.web.wechat.com"

        self.wx_filehost = o
        conf = {
            'LANG': Constant.API_LANG,
            'SpecialUsers': Constant.API_SPECIAL_USER,
            'API_jsLogin': "https://" + t + "/jslogin",
            'API_qrcode': "https://login.weixin.qq.com/l/",
            'API_qrcode_img': "https://login.weixin.qq.com/qrcode/",
            'API_login': "https://" + t + "/cgi-bin/mmwebwx-bin/login",
            'API_synccheck': "https://" + n + "/cgi-bin/mmwebwx-bin/synccheck",
            'API_webwxdownloadmedia': "https://" + o + "/cgi-bin/mmwebwx-bin/webwxgetmedia",
            'API_webwxuploadmedia': "https://" + o + "/cgi-bin/mmwebwx-bin/webwxuploadmedia",
            'API_webwxpreview': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxpreview",
            'API_webwxinit': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxinit",
            'API_webwxgetcontact': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetcontact",
            'API_webwxsync': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsync",
            'API_webwxbatchgetcontact': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxbatchgetcontact",
            'API_webwxgeticon': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgeticon",
            'API_webwxsendmsg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendmsg",
            'API_webwxsendmsgimg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendmsgimg",
            'API_webwxsendmsgvedio': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendvideomsg",
            'API_webwxsendemoticon': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendemoticon",
            'API_webwxsendappmsg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendappmsg",
            'API_webwxgetheadimg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetheadimg",
            'API_webwxgetmsgimg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetmsgimg",
            'API_webwxgetmedia': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetmedia",
            'API_webwxgetvideo': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetvideo",
            'API_webwxlogout': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxlogout",
            'API_webwxgetvoice': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxgetvoice",
            'API_webwxupdatechatroom': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxupdatechatroom",
            'API_webwxcreatechatroom': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxcreatechatroom",
            'API_webwxstatusnotify': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxstatusnotify",
            'API_webwxcheckurl': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxcheckurl",
            'API_webwxverifyuser': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxverifyuser",
            'API_webwxfeedback': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsendfeedback",
            'API_webwxreport': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxstatreport",
            'API_webwxsearch': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxsearchcontact",
            'API_webwxoplog': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxoplog",
            'API_checkupload': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxcheckupload",
            'API_webwxrevokemsg': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxrevokemsg",
            'API_webwxpushloginurl': "https://" + e + "/cgi-bin/mmwebwx-bin/webwxpushloginurl",
            'CONTACTFLAG_CONTACT': 1,
            'CONTACTFLAG_CHATCONTACT': 2,
            'CONTACTFLAG_CHATROOMCONTACT': 4,
            'CONTACTFLAG_BLACKLISTCONTACT': 8,
            'CONTACTFLAG_DOMAINCONTACT': 16,
            'CONTACTFLAG_HIDECONTACT': 32,
            'CONTACTFLAG_FAVOURCONTACT': 64,
            'CONTACTFLAG_3RDAPPCONTACT': 128,
            'CONTACTFLAG_SNSBLACKLISTCONTACT': 256,
            'CONTACTFLAG_NOTIFYCLOSECONTACT': 512,
            'CONTACTFLAG_TOPCONTACT': 2048,
            'MSGTYPE_TEXT': 1,
            'MSGTYPE_IMAGE': 3,
            'MSGTYPE_VOICE': 34,
            'MSGTYPE_VIDEO': 43,
            'MSGTYPE_MICROVIDEO': 62,
            'MSGTYPE_EMOTICON': 47,
            'MSGTYPE_APP': 49,
            'MSGTYPE_VOIPMSG': 50,
            'MSGTYPE_VOIPNOTIFY': 52,
            'MSGTYPE_VOIPINVITE': 53,
            'MSGTYPE_LOCATION': 48,
            'MSGTYPE_STATUSNOTIFY': 51,
            'MSGTYPE_SYSNOTICE': 9999,
            'MSGTYPE_POSSIBLEFRIEND_MSG': 40,
            'MSGTYPE_VERIFYMSG': 37,
            'MSGTYPE_SHARECARD': 42,
            'MSGTYPE_SYS': 10000,
            'MSGTYPE_RECALLED': 10002,
            'APPMSGTYPE_TEXT': 1,
            'APPMSGTYPE_IMG': 2,
            'APPMSGTYPE_AUDIO': 3,
            'APPMSGTYPE_VIDEO': 4,
            'APPMSGTYPE_URL': 5,
            'APPMSGTYPE_ATTACH': 6,
            'APPMSGTYPE_OPEN': 7,
            'APPMSGTYPE_EMOJI': 8,
            'APPMSGTYPE_VOICE_REMIND': 9,
            'APPMSGTYPE_SCAN_GOOD': 10,
            'APPMSGTYPE_GOOD': 13,
            'APPMSGTYPE_EMOTION': 15,
            'APPMSGTYPE_CARD_TICKET': 16,
            'APPMSGTYPE_REALTIME_SHARE_LOCATION': 17,
            'APPMSGTYPE_TRANSFERS': 2e3,
            'APPMSGTYPE_RED_ENVELOPES': 2001,
            'APPMSGTYPE_READER_TYPE': 100001,
            'UPLOAD_MEDIA_TYPE_IMAGE': 1,
            'UPLOAD_MEDIA_TYPE_VIDEO': 2,
            'UPLOAD_MEDIA_TYPE_AUDIO': 3,
            'UPLOAD_MEDIA_TYPE_ATTACHMENT': 4,
        }
        self.wx_conf = conf

    def getuuid(self):
        """
        @brief      Gets the uuid just used for login.
        @return     Bool: whether operation succeed.
        """
        url = self.wx_conf['API_jsLogin']
        params = {
            'appid': self.appid,
            'fun': 'new',
            'lang': self.wx_conf['LANG'],
            '_': int(time.time()),
        }
        data = post(url, params, False)
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, data)
        if pm:
            code = pm.group(1)
            self.uuid = pm.group(2)
            return code == '200'
        return False

    def genqrcode(self):
        """
        @brief      outprint the qrcode to stdout on macos/linux
                    or open image on windows
        """
        if sys.platform.startswith('win'):
            url = self.wx_conf['API_qrcode_img'] + self.uuid
            params = {
                't': 'webwx',
                '_': int(time.time())
            }
            data = post(url, params, False)
            if data == '':
                return
            qrcode_path = save_file('qrcode.jpg', data, './')
            os.startfile(qrcode_path)
        else:
            str2qr_terminal(self.wx_conf['API_qrcode'] + self.uuid)

    def waitforlogin(self, tip=1):
        """
        @brief      wait for scaning qrcode to login
        @param      tip   1: wait for scan qrcode
                          0: wait for confirm
        @return     Bool: whether operation succeed
        """
        time.sleep(tip)
        url = self.wx_conf['API_login'] + '?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time()))
        data = get(url)
        pm = re.search(r'window.code=(\d+);', data)
        code = pm.group(1)

        if code == '201':
            return True
        elif code == '200':
            pm = re.search(r'window.redirect_uri="(\S+?)";', data)
            r_uri = pm.group(1) + '&fun=new'
            self.redirect_uri = r_uri
            self.wx_host = r_uri.split('://')[1].split('/')[0]
            self.conf_factory()
            return True
        elif code == '408':
            echo(Constant.LOG_MSG_WAIT_LOGIN_ERR1)
        else:
            echo(Constant.LOG_MSG_WAIT_LOGIN_ERR2)
        return False

    def login(self):
        """
        @brief      login
                    redirect_uri 有效时间是从扫码成功后算起，
                    大概是 300 秒，在此期间可以重新登录，但获取的联系人和群ID会改变
        @return     Bool: whether operation succeed
        """
        data = get(self.redirect_uri)
        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'ret':
                if node.childNodes[0].data != "0":
                    return False
            elif node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            return False

        self.base_request = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.device_id,
        }

        return True

    def webwxinit(self):
        """
        @brief      wechat initial
                    掉线后 300 秒可以重新使用此 api 登录
                    获取的联系人和群ID保持不变
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxinit'] + \
            '?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time())
        )
        params = {
            'BaseRequest': self.base_request
        }
        dic = post(url, params)
        self.User = dic['User']
        self.make_synckey(dic)

        return dic['BaseResponse']['Ret'] == 0

    def webwxstatusnotify(self):
        """
        @brief      notify the mobile phone, this not necessary
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxstatusnotify'] + \
            '?lang=%s&pass_ticket=%s' % (
                self.wx_conf['LANG'], self.pass_ticket
            )
        params = {
            'BaseRequest': self.base_request,
            "Code": 3,
            "FromUserName": self.User['UserName'],
            "ToUserName": self.User['UserName'],
            "ClientMsgId": int(time.time())
        }
        dic = post(url, params)

        return dic['BaseResponse']['Ret'] == 0

    def webwxgetcontact(self):
        """
        @brief      get all contacts: people, group, public user, special user
        @return     Bool: whether operation succeed
        """
        SpecialUsers = self.wx_conf['SpecialUsers']
        url = self.wx_conf['API_webwxgetcontact'] + \
            '?pass_ticket=%s&skey=%s&r=%s' % (
                self.pass_ticket, self.skey, int(time.time())
            )
        dic = post(url, {})

        self.MemberCount = dic['MemberCount']
        self.MemberList = dic['MemberList']
        ContactList = self.MemberList[:]
        GroupList = self.GroupList[:]
        PublicUsersList = self.PublicUsersList[:]
        SpecialUsersList = self.SpecialUsersList[:]

        for i in xrange(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            if Contact['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                ContactList.remove(Contact)
                self.PublicUsersList.append(Contact)
            elif Contact['UserName'] in SpecialUsers:  # 特殊账号
                ContactList.remove(Contact)
                self.SpecialUsersList.append(Contact)
            elif Contact['UserName'].find('@@') != -1:  # 群聊
                ContactList.remove(Contact)
                self.GroupList.append(Contact)
            elif Contact['UserName'] == self.User['UserName']:  # 自己
                ContactList.remove(Contact)
        self.ContactList = ContactList

        return True

    def webwxbatchgetcontact(self, gid_list):
        """
        @brief      get group contacts
        @param      gid_list, The list of group id
        @return     List, list of group contacts
        """
        url = self.wx_conf['API_webwxbatchgetcontact'] + \
            '?type=ex&r=%s&pass_ticket=%s' % (
                int(time.time()), self.pass_ticket
            )
        params = {
            'BaseRequest': self.base_request,
            "Count": len(gid_list),
            "List": [{"UserName": gid, "EncryChatRoomId": ""} for gid in gid_list]
        }
        dic = post(url, params)
        return dic['ContactList']

    def synccheck(self):
        """
        @brief      check whether there's a message
        @return     [retcode, selector]
                    retcode: 0    successful
                             1100 logout
                             1101 login otherwhere
                    selector: 0 nothing
                              2 message
                              6 unkonwn
                              7 webwxsync
        """
        params = {
            'r': int(time.time()),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.device_id,
            'synckey': self.synckey,
            '_': int(time.time()),
        }
        url = self.wx_conf['API_synccheck'] + '?' + urllib.urlencode(params)
        data = get(url)
        reg = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(reg, data)
        retcode = pm.group(1)
        selector = pm.group(2)
        return [retcode, selector]

    def webwxsync(self):
        """
        @brief      sync the messages
        @return     Dict{}
        """
        url = self.wx_conf['API_webwxsync'] + \
            '?sid=%s&skey=%s&pass_ticket=%s' % (
                self.sid, self.skey, self.pass_ticket
            )
        params = {
            'BaseRequest': self.base_request,
            'SyncKey': self.synckey_dic,
            'rr': ~int(time.time())
        }
        dic = post(url, params)

        if dic['BaseResponse']['Ret'] == 0:
            self.make_synckey(dic)
        return dic

    def webwxgetmsgimg(self, msgid):
        """
        @brief      get image in message
        @param      msgid  The id of message
        @return     binary data of image
        """
        url = self.wx_conf['API_webwxgetmsgimg'] + \
            '?MsgID=%s&skey=%s' % (msgid, self.skey)
        data = get(url, api='webwxgetmsgimg')
        return data

    def webwxgetvoice(self, msgid):
        """
        @brief      get voice in message
        @param      msgid  The id of message
        @return     binary data of voice
        """
        url = self.wx_conf['API_webwxgetvoice'] + \
            '?msgid=%s&skey=%s' % (msgid, self.skey)
        data = get(url, api='webwxgetvoice')
        return data

    def webwxgetvideo(self, msgid):
        """
        @brief      get video in message
        @param      msgid  The id of message
        @return     binary data of video
        """
        url = self.wx_conf['API_webwxgetvideo'] + \
            '?msgid=%s&skey=%s' % (msgid, self.skey)
        data = get(url, api='webwxgetvideo')
        return data

    def webwxgeticon(self, id):
        """
        @brief      get user small icon
        @param      id  String
        @return     binary data of icon
        """
        url = self.wx_conf['API_webwxgeticon'] + \
            '?username=%s&skey=%s' % (id, self.skey)
        data = get(url, api='webwxgeticon')
        return data

    def webwxgetheadimg(self, id):
        """
        @brief      get user head image
        @param      id  String
        @return     binary data of image
        """
        url = self.wx_conf['API_webwxgetheadimg'] + \
            '?username=%s&skey=%s' % (id, self.skey)
        data = get(url, api='webwxgetheadimg')
        return data

    def webwxsendmsg(self, word, to='filehelper'):
        """
        @brief      send text message
        @param      word  String
        @param      to    User id
        @return     dic   Dict
        """
        url = self.wx_conf['API_webwxsendmsg'] + \
            '?pass_ticket=%s' % (self.pass_ticket)
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        params = {
            'BaseRequest': self.base_request,
            'Msg': {
                "Type": 1,
                "Content": trans_coding(word),
                "FromUserName": self.User['UserName'],
                "ToUserName": to,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        dic = post(url, params)
        return dic

    def webwxuploadmedia(self, file_path):
        """
        @brief      upload image
        @param      file_path  String
        @return     Dict: json
        """
        url = self.wx_conf['API_webwxuploadmedia'] + '?f=json'
        # 计数器
        self.media_count = self.media_count + 1
        fn = file_path
        # mime_type: 
        #   'application/pdf'
        #   'image/jpeg'
        #   'image/png'
        #   ...
        mime_type = mimetypes.guess_type(fn, strict=False)[0]
        if not mime_type:
            mime_type = 'text/plain'
        # 文档格式
        # 微信服务器目前应该支持3种类型:
        #   pic     直接显示，包含图片，表情
        #   video   不清楚
        #   doc     显示为文件，包含PDF等
        media_type = 'pic' if mime_type.split('/')[0] == 'image' else 'doc'
        time_format = "%a %b %d %Y %T GMT%z (%Z)"
        last_modifie_date = time.strftime(time_format, time.localtime())
        file_size = os.path.getsize(fn)
        pass_ticket = self.pass_ticket
        client_media_id = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')

        webwx_data_ticket = ''
        for item in self.cookie:
            if item.name == 'webwx_data_ticket':
                webwx_data_ticket = item.value
                break
        if (webwx_data_ticket == ''):
            Log.error("No Cookie\n")
            return None

        uploadmediarequest = json.dumps({
            "BaseRequest": self.base_request,
            "ClientMediaId": client_media_id,
            "TotalLen": file_size,
            "StartPos": 0,
            "DataLen": file_size,
            "MediaType": 4
        }, ensure_ascii=False).encode('utf8')

        multipart_encoder = MultipartEncoder(
            fields={
                'id': 'WU_FILE_' + str(self.media_count),
                'name': fn,
                'type': mime_type,
                'lastModifieDate': last_modifie_date,
                'size': str(file_size),
                'mediatype': media_type,
                'uploadmediarequest': uploadmediarequest,
                'webwx_data_ticket': webwx_data_ticket,
                'pass_ticket': pass_ticket,
                'filename': (
                    fn,
                    open(fn, 'rb'),
                    mime_type.split('/')[1]
                )
            },
            boundary=(
                '-----------------------------'
                '1575017231431605357584454111'
            )
        )

        headers = {
            'Host': self.wx_filehost,
            'User-Agent': self.user_agent,
            'Accept': (
                'text/html,application/xhtml+xml,'
                'application/xml;q=0.9,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://' + self.wx_host,
            'Content-Type': multipart_encoder.content_type,
            'Origin': 'https://' + self.wx_host,
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        r = requests.post(url, data=multipart_encoder, headers=headers)
        dic = json.loads(r.text)  #修复无法发送Media消息BUG
        if dic['BaseResponse']['Ret'] == 0:
            return dic
        return None

    def webwxsendmsgimg(self, user_id, media_id):
        """
        @brief      send image
        @param      user_id  String
        @param      media_id  String
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxsendmsgimg'] + \
            '?fun=async&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.base_request,
            "Msg": {
                "Type": 3,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        r = post(url, data_json)
        return dic['BaseResponse']['Ret'] == 0

    def webwxsendemoticon(self, user_id, media_id):
        """
        @brief      send image
        @param      user_id  String
        @param      media_id  String
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxsendemoticon'] + \
            '?fun=sys&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.base_request,
            "Msg": {
                "Type": 47,
                "EmojiFlag": 2,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        r = post(url, data_json)
        return dic['BaseResponse']['Ret'] == 0

    def webwxsendappmsg(self, user_id, data):
        """
        @brief      send app msg
        @param      user_id  String
        @param      data     Dict
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxsendappmsg'] + \
            '?fun=sys&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        content = ''.join([
            "<appmsg appid='%s' sdkver=''>" % data['appid'], # 可使用其它AppID
                "<title>%s</title>" % data['title'],
                "<des></des>",
                "<action></action>",
                "<type>%d</type>" % data['type'],
                "<content></content>",
                "<url></url>",
                "<lowurl></lowurl>",
                "<appattach>",
                    "<totallen>%d</totallen>" % data['totallen'],
                    "<attachid>%s</attachid>" % data['attachid'],
                    "<fileext>%s</fileext>" % data['fileext'],
                "</appattach>",
                "<extinfo></extinfo>",
            "</appmsg>",
        ])
        data_json = {
            "BaseRequest": self.base_request,
            "Msg": {
                "Type": data['type'],
                "Content": content,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            },
            "Scene": 0
        }
        r = post(url, data_json)
        return dic['BaseResponse']['Ret'] == 0

    def webwxcreatechatroom(self, uid_arr):
        """
        @brief      create a chat group
        @param      uid_arr  [String]
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxcreatechatroom'] + '?r=%s' % int(time.time())
        params = {
            'BaseRequest': self.base_request,
            'Topic': '',
            'MemberCount': len(uid_arr),
            'MemberList': [{'UserName': uid} for uid in uid_arr],
        }
        dic = post(url, params)
        return dic['BaseResponse']['Ret'] == 0

    def webwxupdatechatroom(self, add_arr, del_arr, invite_arr):
        """
        @brief      add/delete/invite member in chat group
        @param      add_arr     [uid: String]
        @param      del_arr     [uid: String]
        @param      invite_arr  [uid: String]
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxupdatechatroom'] + '?r=%s' % int(time.time())
        params = {
            'BaseRequest': self.base_request,
            'ChatRoomName': '',
            'NewTopic': '',
            'AddMemberList': add_arr,
            'DelMemberList': del_arr,
            'InviteMemberList': invite_arr,
        }
        dic = post(url, params)
        return dic['BaseResponse']['Ret'] == 0

    def webwxrevokemsg(self, msgid, user_id, client_msgid):
        """
        @brief      revoke a message
        @param      msgid           String
        @param      user_id         String
        @param      client_msgid    String
        @return     Bool: whether operation succeed
        """
        url = self.wx_conf['API_webwxrevokemsg'] + '?r=%s' % int(time.time())
        params = {
            'BaseRequest': self.base_request,
            'SvrMsgId': msgid,
            'ToUserName': user_id,
            'ClientMsgId': client_msgid
        }
        dic = post(url, params)
        return dic['BaseResponse']['Ret'] == 0

    def webwxpushloginurl(self, uin):
        """
        @brief      push a login confirm alert to mobile device
        @param      uin   String
        @return     dic   Dict
        """
        url = self.wx_conf['API_webwxpushloginurl'] + '?uin=%s' % uin
        dic = eval(get(url))
        return dic

    def association_login(self):
        """
        @brief      login without scan qrcode
        @return     Bool: whether operation succeed
        """
        if self.uin != '':
            dic = self.webwxpushloginurl(self.uin)
            if dic['ret'] == '0':
                self.uuid = dic['uuid']
                return True
        return False

    def send_text(self, user_id, text):
        """
        @brief      send text
        @param      user_id  String
        @param      text  String
        @return     Bool: whether operation succeed
        """
        try:
            dic = self.webwxsendmsg(text, user_id)
            return dic['BaseResponse']['Ret'] == 0
        except:
            return False

    def send_img(self, user_id, file_path):
        """
        @brief      send image
        @param      user_id  String
        @param      file_path  String
        @return     Bool: whether operation succeed
        """
        response = self.webwxuploadmedia(file_path)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        return self.webwxsendmsgimg(user_id, media_id)

    def send_emot(self, user_id, file_path):
        """
        @brief      send emotion
        @param      user_id  String
        @param      file_path  String
        @return     Bool: whether operation succeed
        """
        response = self.webwxuploadmedia(file_path)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        return self.webwxsendemoticon(user_id, media_id)

    def send_file(self, user_id, file_path):
        """
        @brief      send file
        @param      user_id  String
        @param      file_path  String
        @return     Bool: whether operation succeed
        """
        title = file_path.split('/')[-1]
        data = {
            'appid': Constant.API_WXAPPID,
            'title': title,
            'totallen': '',
            'attachid': '',
            'type': self.wx_conf['APPMSGTYPE_ATTACH'],
            'fileext': title.split('.')[-1],
        }

        response = self.webwxuploadmedia(file_path)
        if response is not None:
            data['totallen'] = response['StartPos']
            data['attachid'] = response['MediaId']
        else:
            Log.error('File upload error')
        
        return self.webwxsendappmsg(user_id, data)

    def make_synckey(self, dic):
        self.synckey_dic = dic['SyncKey']

        def foo(x):
            return str(x['Key']) + '_' + str(x['Val'])

        # synckey for synccheck
        self.synckey = '|'.join(
            [foo(keyVal) for keyVal in self.synckey_dic['List']])

    def revoke_msg(self, msgid, user_id, client_msgid):
        """
        @brief      revoke a message
        @param      msgid           String
        @param      user_id         String
        @param      client_msgid    String
        @return     Bool: whether operation succeed
        """
        return self.webwxrevokemsg(msgid, user_id, client_msgid)

    # -----------------------------------------------------
    # The following is getting user & group infomation apis
    def get_user_by_id(self, user_id):
        """
        @brief      get all type of name by user id
        @param      user_id  The id of user
        @return     Dict: {
                        'UserName'      # 微信动态ID
                        'RemarkName'    # 备注
                        'NickName'      # 微信昵称
                        'ShowName'      # Log显示用的
                    }
        """
        UnknownPeople = Constant.LOG_MSG_UNKNOWN_NAME + user_id
        name = {
            'UserName': user_id,
            'RemarkName': '',
            'NickName': '',
            'ShowName': '',
        }
        name['ShowName'] = UnknownPeople

        # yourself
        if user_id == self.User['UserName']:
            name['RemarkName'] = self.User['RemarkName']
            name['NickName'] = self.User['NickName']
            name['ShowName'] = name['NickName']
        else:
            # 联系人
            for member in self.MemberList:
                if member['UserName'] == user_id:
                    r, n = member['RemarkName'], member['NickName']
                    name['RemarkName'] = r
                    name['NickName'] = n
                    name['ShowName'] = r if r else n
                    break
            # 特殊帐号
            for member in self.SpecialUsersList:
                if member['UserName'] == user_id:
                    name['RemarkName'] = user_id
                    name['NickName'] = user_id
                    name['ShowName'] = user_id
                    break

        return name

    def get_group_user_by_id(self, user_id, group_id):
        """
        @brief      get group user by user id
        @param      user_id  The id of user
        @param      group_id  The id of group
        @return     Dict: {
                        'UserName'      # 微信动态ID
                        'NickName'      # 微信昵称
                        'DisplayName'   # 群聊显示名称
                        'ShowName'      # Log显示用的
                        'AttrStatus'    # 群用户id
                    }
        """
        UnknownPeople = Constant.LOG_MSG_UNKNOWN_NAME + user_id
        name = {
            'UserName': user_id,
            'NickName': '',
            'DisplayName': '',
            'ShowName': '',
            'AttrStatus': '',
        }
        name['ShowName'] = UnknownPeople

        # 群友
        if group_id in self.GroupMemeberList:
            for member in self.GroupMemeberList[group_id]:
                if member['UserName'] == user_id:
                    n, d = member['NickName'], member['DisplayName']
                    name['NickName'] = n
                    name['DisplayName'] = d
                    name['AttrStatus'] = member['AttrStatus']
                    name['ShowName'] = d if d else n
                    break

        return name

    def get_group_by_id(self, group_id):
        """
        @brief      get basic info by group id
        @param      group_id  The id of group
        @return     Dict: {
                        'UserName'      # 微信动态ID
                        'NickName'      # 微信昵称
                        'DisplayName'   # 群聊显示名称
                        'ShowName'      # Log显示用的
                        'OwnerUin'      # 群主ID
                        'MemberCount'   # 群人数
                    }
        """
        UnknownGroup = Constant.LOG_MSG_UNKNOWN_GROUP_NAME + group_id
        group = {
            'UserName': group_id,
            'NickName': '',
            'DisplayName': '',
            'ShowName': '',
            'OwnerUin': '',
            'MemberCount': '',
        }

        for member in self.GroupList:
            if member['UserName'] == group_id:
                group['NickName'] = member['NickName']
                group['DisplayName'] = member.get('DisplayName', '')
                group['ShowName'] = member.get('NickName', UnknownGroup)
                group['OwnerUin'] = member.get('OwnerUin', '')
                group['MemberCount'] = member['MemberCount']
                break

        return group

    def get_user_id(self, name):
        """
        @brief      Gets the user id.
        @param      name  The user nickname or remarkname
        @return     The user id.
        """
        for member in self.MemberList:
            if name == member['RemarkName'] or name == member['NickName']:
                return member['UserName']
        return None
