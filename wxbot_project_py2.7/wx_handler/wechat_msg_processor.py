#!/usr/bin/env python
# coding: utf-8

#===================================================
from wechat.utils import *
from config import ConfigManager
from config import Constant
from config import Log
#---------------------------------------------------
import os
import time
import json
import re
#===================================================


class WeChatMsgProcessor(object):
    """
    Process fetched data
    """

    def __init__(self, db):
        self.db = db
        self.wechat = None  # recieve `WeChat` class instance
                            # for call some wechat apis

        # read config
        cm = ConfigManager()
        [self.upload_dir, self.data_dir, self.log_dir] = cm.setup_database()

    def clean_db(self):
        """
        @brief clean database, delete table & create table
        """
        self.db.delete_table(Constant.TABLE_GROUP_LIST())
        self.db.delete_table(Constant.TABLE_GROUP_USER_LIST())
        self.db.create_table(Constant.TABLE_GROUP_MSG_LOG, Constant.TABLE_GROUP_MSG_LOG_COL)
        self.db.create_table(Constant.TABLE_GROUP_LIST(), Constant.TABLE_GROUP_LIST_COL)
        self.db.create_table(Constant.TABLE_GROUP_USER_LIST(), Constant.TABLE_GROUP_USER_LIST_COL)
        self.db.create_table(Constant.TABLE_RECORD_ENTER_GROUP, Constant.TABLE_RECORD_ENTER_GROUP_COL)
        self.db.create_table(Constant.TABLE_RECORD_RENAME_GROUP, Constant.TABLE_RECORD_RENAME_GROUP_COL)

    def handle_wxsync(self, msg):
        """
        @brief      Recieve webwxsync message, saved into json
        @param      msg  Dict: webwxsync msg
        """
        fn = time.strftime(Constant.LOG_MSG_FILE, time.localtime())
        save_json(fn, msg, self.log_dir, 'a+')

    def handle_group_list(self, group_list):
        """
        @brief      handle group list & saved in DB
        @param      group_list  Array
        """
        fn = Constant.LOG_MSG_GROUP_LIST_FILE
        save_json(fn, group_list, self.data_dir)
        cols = [(
            g['NickName'],
            g['UserName'],
            g['OwnerUin'],
            g['MemberCount'],
            g['HeadImgUrl']
        ) for g in group_list]
        self.db.insertmany(Constant.TABLE_GROUP_LIST(), cols)

    def handle_group_member_list(self, group_id, member_list):
        """
        @brief      handle group member list & saved in DB
        @param      member_list  Array
        """
        fn = group_id + '.json'
        save_json(fn, member_list, self.data_dir)
        cols = [(
            group_id,
            m['UserName'],
            m['NickName'],
            m['DisplayName'],
            m['AttrStatus']
        ) for m in member_list]
        self.db.insertmany(Constant.TABLE_GROUP_USER_LIST(), cols)

    def handle_group_list_change(self, new_group):
        """
        @brief      handle adding a new group & saved in DB
        @param      new_group  Dict
        """
        self.handle_group_list([new_group])

    def handle_group_member_change(self, group_id, member_list):
        """
        @brief      handle group member changes & saved in DB
        @param      group_id  Dict
        @param      member_list  Dict
        """
        self.db.delete(Constant.TABLE_GROUP_USER_LIST(), "RoomID", group_id)
        self.handle_group_member_list(group_id, member_list)

    def handle_group_msg(self, msg):
        """
        @brief      Recieve group messages
        @param      msg  Dict: packaged msg
        """
        # rename media files
        for k in ['image', 'video', 'voice']:
            if msg[k]:
                t = time.localtime(float(msg['timestamp']))
                time_str = time.strftime("%Y%m%d%H%M%S", t)
                # format: 时间_消息ID_群名
                file_name = '/%s_%s_%s.' % (time_str, msg['msg_id'], msg['group_name'])
                new_name = re.sub(r'\/\w+\_\d+\.', file_name, msg[k])
                Log.debug('rename file to %s' % new_name)
                os.rename(msg[k], new_name)
                msg[k] = new_name

        if msg['msg_type'] == 10000:
            # record member enter in group
            m = re.search(r'邀请(.+)加入了群聊', msg['sys_notif'])
            if m:
                name = m.group(1)
                col_enter_group = (
                    msg['msg_id'],
                    msg['group_name'],
                    msg['from_user_name'],
                    msg['to_user_name'],
                    name,
                    msg['time'],
                )
                self.db.insert(Constant.TABLE_RECORD_ENTER_GROUP, col_enter_group)

            # record rename group
            n = re.search(r'(.+)修改群名为“(.+)”', msg['sys_notif'])
            if n:
                people = n.group(1)
                to_name = n.group(2)
                col_rename_group = (
                    msg['msg_id'],
                    msg['group_name'],
                    to_name,
                    people,
                    msg['time'],
                )
                self.db.insert(Constant.TABLE_RECORD_RENAME_GROUP, col_rename_group)
                
                # upadte group in GroupList
                for g in self.wechat.GroupList:
                    if g['UserName'] == msg['from_user_name']:
                        g['NickName'] = to_name
                        break

        # normal group message
        col = (
            msg['msg_id'],
            msg['group_owner_uin'],
            msg['group_name'],
            msg['group_count'],
            msg['from_user_name'],
            msg['to_user_name'],
            msg['user_attrstatus'],
            msg['user_display_name'],
            msg['user_nickname'],
            msg['msg_type'],
            msg['emoticon'],
            msg['text'],
            msg['image'],
            msg['video'],
            msg['voice'],
            msg['link'],
            msg['namecard'],
            msg['location'],
            msg['recall_msg_id'],
            msg['sys_notif'],
            msg['time'],
            msg['timestamp']
        )
        self.db.insert(Constant.TABLE_GROUP_MSG_LOG, col)

        text = msg['text']
        if text and text[0] == '@':
            n = trans_coding(text).find(u'\u2005')
            name = trans_coding(text)[1:n].encode('utf-8')
            if name in [self.wechat.User['NickName'], self.wechat.User['RemarkName']]:
                self.handle_command(trans_coding(text)[n+1:].encode('utf-8'), msg)

    def handle_user_msg(self, msg):
        """
        @brief      Recieve personal messages
        @param      msg  Dict
        """
        wechat = self.wechat

        text = trans_coding(msg['text']).encode('utf-8')
        uid = msg['raw_msg']['FromUserName']

        if text == 'test_revoke': # 撤回消息测试
            dic = wechat.webwxsendmsg('这条消息将被撤回', uid)
            wechat.revoke_msg(dic['MsgID'], uid, dic['LocalID'])
        elif text == 'reply':
            wechat.send_text(uid, '自动回复')


    def handle_command(self, cmd, msg):
        """
        @brief      handle msg of `@yourself cmd`
        @param      cmd   String
        @param      msg   Dict
        """
        wechat = self.wechat
        g_id = ''
        for g in wechat.GroupList:
            if g['NickName'] == msg['group_name']:
                g_id = g['UserName']

        cmd = cmd.strip()
        if cmd == 'runtime':
            wechat.send_text(g_id, wechat.get_run_time())
        elif cmd == 'test_sendimg':
            wechat.send_img(g_id, 'test/emotion/7.gif')
        elif cmd == 'test_sendfile':
            wechat.send_file(g_id, 'test/Data/upload/shake.wav')
        elif cmd == 'test_bot':
            # reply bot
            # ---------
            if wechat.bot:
                r = wechat.bot.reply(cmd)
                if r:
                    wechat.send_text(g_id, r)
                else:
                    pass
        elif cmd == 'test_emot':
            img_name = [
                '0.jpg', '1.jpeg', '2.gif', '3.jpg', '4.jpeg',
                '5.gif', '6.gif', '7.gif', '8.jpg', '9.jpg'
            ]
            name = img_name[int(time.time()) % 10]
            emot_path = os.path.join('test/emotion/', name)
            wechat.send_emot(g_id, emot_path)
        else:
            pass

    def check_schedule_task(self):
        # update group member list at 00:00 am every morning
        t = time.localtime()
        if t.tm_hour == 0 and t.tm_min <= 1:
            # update group member
            Log.debug('update group member list everyday')
            self.db.delete_table(Constant.TABLE_GROUP_LIST())
            self.db.delete_table(Constant.TABLE_GROUP_USER_LIST())
            self.db.create_table(Constant.TABLE_GROUP_LIST(), Constant.TABLE_GROUP_LIST_COL)
            self.db.create_table(Constant.TABLE_GROUP_USER_LIST(), Constant.TABLE_GROUP_USER_LIST_COL)
            self.wechat.fetch_group_contacts()

