#!/usr/bin/env python
# coding: utf-8

#===================================================
from constant import Constant
#---------------------------------------------------
import ConfigParser
import os
#===================================================


class ConfigManager(object):

    def __init__(self):
        self.config = Constant.WECHAT_CONFIG_FILE
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(self.config)

        data_dir = self.get('setting', 'prefix')
        upload_dir = self.getpath('uploaddir')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

    def get(self, section, option):
        return self.cp.get(section, option)

    def set(self, section, option, value):
        self.cp.set(section, option, value)
        self.cp.write(open(self.config, 'w'))

    def getpath(self, dir):
        prefix = self.get('setting', 'prefix')
        return prefix + self.get('setting', dir)

    def setup_database(self):
        path = self.get('setting', 'prefix')
        conf = [
            path + self.get('setting', 'uploaddir'),
            path + self.get('setting', 'datadir'),
            path + self.get('setting', 'logdir'),
        ]
        return conf

    def set_wechat_config(self, conf):
        for [key, value] in conf.items():
            self.cp.set('wechat', key, value)
        self.cp.write(open(self.config, 'w'))

    def get_wechat_config(self):
        uin = self.cp.get('wechat', 'uin')
        last_login = self.cp.get('wechat', 'last_login')
        conf = [
            self.cp.get('wechat', 'uuid'),
            self.cp.get('wechat', 'redirect_uri'),
            int(uin if uin else 0),
            self.cp.get('wechat', 'sid'),
            self.cp.get('wechat', 'skey'),
            self.cp.get('wechat', 'pass_ticket'),
            self.cp.get('wechat', 'synckey'),
            self.cp.get('wechat', 'device_id'),
            float(last_login if last_login else 0),
        ]
        return conf

    def get_wechat_media_dir(self):
        prefix = self.get('setting', 'prefix')
        path = prefix + self.cp.get('setting', 'mediapath')
        return {
            'webwxgeticon': path + '/icons',
            'webwxgetheadimg': path + '/headimgs',
            'webwxgetmsgimg': path + '/msgimgs',
            'webwxgetvideo': path + '/videos',
            'webwxgetvoice': path + '/voices',
            '_showQRCodeImg': path + '/qrcodes',
        }

    def get_pickle_files(self):
        prefix = self.get('setting', 'prefix')
        return {
            'User': prefix + self.get('setting', 'contact_user'),
            'MemberList': prefix + self.get('setting', 'contact_member_list'),
            'GroupList': prefix + self.get('setting', 'contact_group_list'),
            'GroupMemeberList': prefix + self.get('setting', 'contact_group_memeber_list'),
            'SpecialUsersList': prefix + self.get('setting', 'contact_special_users_list'),
        }

    def get_cookie(self):
        prefix = self.get('setting', 'prefix')
        path = prefix + self.get('setting', 'cookie')
        basedir = os.path.dirname(path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        return path

    def mysql(self):
        mysql = {
            'host': self.get('mysql', 'host'),
            'port': self.cp.getint('mysql', 'port'),
            'user': self.get('mysql', 'user'),
            'passwd': self.get('mysql', 'passwd'),
            'database': self.get('mysql', 'database'),
        }
        return mysql
