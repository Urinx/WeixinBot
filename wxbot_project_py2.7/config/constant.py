#!/usr/bin/env python
# coding: utf-8
import time

class Constant(object):
    """
    @brief      All used constants are listed here
    """

    WECHAT_CONFIG_FILE = 'config/wechat.conf'
    LOGGING_LOGGER_NAME = 'WeChat'

    QRCODE_BLACK = '\033[40m  \033[0m'
    QRCODE_WHITE = '\033[47m  \033[0m'

    HTTP_HEADER_USERAGENT = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36')]
    HTTP_HEADER_CONTENTTYPE = ['ContentType', 'application/json; charset=UTF-8']
    HTTP_HEADER_CONNECTION = ['Connection', 'keep-alive']
    HTTP_HEADER_REFERER = ['Referer', 'https://wx.qq.com/']
    HTTP_HEADER_RANGE = ['Range', 'bytes=0-']

    REGEX_EMOJI = r'<span class="emoji emoji(\w+)"></span>'
    
    SERVER_LOG_FORMAT = '%(asctime)s - %(pathname)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s'
    SERVER_UPLOAD_ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    SERVER_PAGE_UPLOAD = 'upload.html'
    SERVER_PAGE_INDEX = 'index.html'

    RUN_RESULT_SUCCESS = '成功 %ds\n'
    RUN_RESULT_FAIL = '失败\n[*] 退出程序\n'
    MAIN_RESTART = '[*] wait for restart'
    LOG_MSG_FILE = 'WeChat-Msgs-%Y-%m-%d.json'
    LOG_MSG_GROUP_LIST_FILE = 'group_list.json'
    LOG_MSG_QUIT = '\n[*] Force quit.\n'
    LOG_MSG_FAIL = '失败\n'
    LOG_MSG_SUCCESS = '成功\n'
    LOG_MSG_START = '[*] 微信网页版 ... 开动\n'
    LOG_MSG_RECOVER = '[*] 从配置文件中恢复 ... '
    LOG_MSG_RECOVER_CONTACT = '[*] 从文件中恢复联系人数据 ... '
    LOG_MSG_TRY_INIT = '[*] 尝试初始化 ... '
    LOG_MSG_ASSOCIATION_LOGIN = '[*] 通过关联登录 ... '
    LOG_MSG_GET_UUID = '[*] 正在获取 uuid ... '
    LOG_MSG_GET_QRCODE = '[*] 正在获取二维码 ... 成功\n'
    LOG_MSG_SCAN_QRCODE = '[*] 请使用微信扫描二维码以登录 ... \n'
    LOG_MSG_CONFIRM_LOGIN = '[*] 请在手机上点击确认以登录 ... \n'
    LOG_MSG_WAIT_LOGIN_ERR1 = '[登陆超时] \n'
    LOG_MSG_WAIT_LOGIN_ERR2 = '[登陆异常] \n'
    LOG_MSG_LOGIN = '[*] 正在登录 ... '
    LOG_MSG_INIT = '[*] 微信初始化 ... '
    LOG_MSG_STATUS_NOTIFY = '[*] 开启状态通知 ... '
    LOG_MSG_GET_CONTACT = '[*] 获取联系人 ... '
    LOG_MSG_CONTACT_COUNT = '[*] 应有 %s 个联系人，读取到联系人 %d 个\n'
    LOG_MSG_OTHER_CONTACT_COUNT = '[*] 共有 %d 个群 | %d 个直接联系人 | %d 个特殊账号 ｜ %d 公众号或服务号\n'
    LOG_MSG_GET_GROUP_MEMBER = '[*] 拉取群聊成员 ... '
    LOG_MSG_SNAPSHOT = '[*] 保存配置 ... '
    LOG_MSG_LOGOUT = '[*] 你在手机上登出了微信\n'
    LOG_MSG_LOGIN_OTHERWHERE = '[*] 你在其他地方登录了 WEB 版微信\n'
    LOG_MSG_QUIT_ON_PHONE = '[*] 你在手机上主动退出了\n'
    LOG_MSG_RUNTIME = '[*] Total run: %s\n'
    LOG_MSG_KILL_PROCESS = 'kill %d'
    LOG_MSG_NEW_MSG = '>>> %d 条新消息\n'
    LOG_MSG_LOCATION = '[位置] %s'
    LOG_MSG_PICTURE = '[图片] %s'
    LOG_MSG_VOICE = '[语音] %s'
    LOG_MSG_RECALL = '撤回了一条消息'
    LOG_MSG_ADD_FRIEND = '%s 请求添加你为好友'
    LOG_MSG_UNKNOWN_MSG = '[*] 该消息类型为: %d，内容: %s'
    LOG_MSG_VIDEO = '[小视频] %s'
    LOG_MSG_NOTIFY_PHONE = '[*] 提示手机网页版微信登录状态\n'
    LOG_MSG_EMOTION = '[表情] %s'
    LOG_MSG_NAME_CARD = (
        '[名片]\n'
        '=========================\n'
        '= 昵称: %s\n'
        '= 微信号: %s\n'
        '= 地区: %s %s\n'
        '= 性别: %s\n'
        '========================='
    )
    LOG_MSG_SEX_OPTION = ['未知', '男', '女']
    LOG_MSG_APP_LINK = (
        '[%s]\n'
        '=========================\n'
        '= 标题: %s\n'
        '= 描述: %s\n'
        '= 链接: %s\n'
        '= 来自: %s\n'
        '========================='
    )
    LOG_MSG_APP_LINK_TYPE = {5: '链接', 3: '音乐', 7: '微博'}
    LOG_MSG_APP_IMG = (
        '[图片]\n'
        '=========================\n'
        '= 文件: %s\n'
        '= 来自: %s\n'
        '========================='
    )
    LOG_MSG_SYSTEM = '系统消息'
    LOG_MSG_UNKNOWN_NAME = '未知_'
    LOG_MSG_UNKNOWN_GROUP_NAME = '未知群_'

    TABLE_GROUP_MSG_LOG = 'WeChatRoomMessage'
    TABLE_GROUP_MSG_LOG_COL = """
        MsgID text,
        RoomOwnerID text,
        RoomName text,
        UserCount text,
        FromUserName text,
        ToUserName text,
        AttrStatus text,
        DisplayName text,
        Name text, 
        MsgType text,
        FaceMsg text,
        TextMsg text,
        ImageMsg text,
        VideoMsg text,
        SoundMsg text,
        LinkMsg text,
        NameCardMsg text,
        LocationMsg text,
        RecallMsgID text,
        SysMsg text,
        MsgTime text,
        MsgTimestamp text
    """

    @staticmethod
    def TABLE_GROUP_LIST():
        return 'WeChatRoom_' + time.strftime('%Y%m%d', time.localtime())
    
    TABLE_GROUP_LIST_COL = """
        RoomName text,
        RoomID text,
        RoomOwnerID text,
        UserCount text,
        RoomIcon text
    """

    @staticmethod
    def TABLE_GROUP_USER_LIST():
        return 'WeChatRoomMember_' + time.strftime('%Y%m%d', time.localtime())

    TABLE_GROUP_USER_LIST_COL = """
        RoomID text,
        MemberID text,
        MemberNickName text,
        MemberDisplayName text,
        MemberAttrStatus text
    """
    TABLE_RECORD_ENTER_GROUP = 'WeChatEnterGroupRecord'
    TABLE_RECORD_ENTER_GROUP_COL = """
        MsgID text,
        RoomName text,
        FromUserName text,
        ToUserName text,
        Name text,
        EnterTime text
    """
    TABLE_RECORD_RENAME_GROUP = 'WeChatRenameGroupRecord'
    TABLE_RECORD_RENAME_GROUP_COL = """
        MsgID text,
        FromName text,
        ToName text,
        ModifyPeople text,
        ModifyTime text
    """

    API_APPID = 'wx782c26e4c19acffb'
    API_WXAPPID = 'wx299208e619de7026' # Weibo
                # 'wxeb7ec651dd0aefa9' # Weixin
    API_LANG = 'zh_CN'
    API_USER_AGENT = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/48.0.2564.109 Safari/537.36'
    )
    API_SPECIAL_USER = [
        'newsapp', 'filehelper', 'weibo', 'qqmail',
        'fmessage', 'tmessage', 'qmessage', 'qqsync',
        'floatbottle', 'lbsapp', 'shakeapp', 'medianote',
        'qqfriend', 'readerapp', 'blogapp', 'facebookapp',
        'masssendapp', 'meishiapp', 'feedsapp', 'voip',
        'blogappweixin', 'brandsessionholder', 'weixin',
        'weixinreminder', 'officialaccounts', 'wxitil',
        'notification_messages', 'wxid_novlwrv3lqwv11',
        'gh_22b87fa7cb3c', 'userexperience_alarm',
    ]

    EMOTICON = [
        '[Smile]', '[Grimace]', '[Drool]', '[Scowl]', '[CoolGuy]', '[Sob]', '[Shy]',
        '[Silent]', '[Sleep]', '[Cry]', '[Awkward]', '[Angry]', '[Tongue]', '[Grin]',
        '[Surprise]', '[Frown]', '[Ruthless]', '[Blush]', '[Scream]', '[Puke]',
        '[Chuckle]', '[Joyful]', '[Slight]', '[Smug]', '[Hungry]', '[Drowsy]', '[Panic]',
        '[Sweat]', '[Laugh]', '[Commando]', '[Determined]', '[Scold]', '[Shocked]', '[Shhh]',
        '[Dizzy]', '[Tormented]', '[Toasted]', '[Skull]', '[Hammer]', '[Wave]',
        '[Relief]', '[DigNose]', '[Clap]', '[Shame]', '[Trick]',' [Bah！L]','[Bah！R]',
        '[Yawn]', '[Lookdown]', '[Wronged]', '[Puling]', '[Sly]', '[Kiss]', '[Uh-oh]',
        '[Whimper]', '[Cleaver]', '[Melon]', '[Beer]', '[Basketball]', '[PingPong]',
        '[Coffee]', '[Rice]', '[Pig]', '[Rose]', '[Wilt]', '[Lip]', '[Heart]',
        '[BrokenHeart]', '[Cake]', '[Lightning]', '[Bomb]', '[Dagger]', '[Soccer]', '[Ladybug]',
        '[Poop]', '[Moon]', '[Sun]', '[Gift]', '[Hug]', '[Strong]',
        '[Weak]', '[Shake]', '[Victory]', '[Admire]', '[Beckon]', '[Fist]', '[Pinky]',
        '[Love]', '[No]', '[OK]', '[InLove]', '[Blowkiss]', '[Waddle]', '[Tremble]',
        '[Aaagh!]', '[Twirl]', '[Kotow]', '[Lookback]', '[Jump]', '[Give-in]',
        u'\U0001f604', u'\U0001f637', u'\U0001f639', u'\U0001f61d', u'\U0001f632', u'\U0001f633',
        u'\U0001f631', u'\U0001f64d', u'\U0001f609', u'\U0001f60c', u'\U0001f612', u'\U0001f47f',
        u'\U0001f47b', u'\U0001f49d', u'\U0001f64f', u'\U0001f4aa', u'\U0001f4b5', u'\U0001f382',
        u'\U0001f388', u'\U0001f4e6',
    ]
    BOT_ZHIHU_URL_LATEST = 'http://news-at.zhihu.com/api/4/news/latest'
    BOT_ZHIHU_URL_DAILY = 'http://daily.zhihu.com/story/'
    BOT_TULING_API_KEY = '55e7f30895a0a10535984bae5ad294d1'
    BOT_TULING_API_URL = 'http://www.tuling123.com/openapi/api?key=%s&info=%s&userid=%s'
    BOT_TULING_BOT_REPLY = u'麻烦说的清楚一点，我听不懂你在说什么'
