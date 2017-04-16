#!/usr/bin/env python
# coding: utf-8

#===================================================
from wechat.utils import *
from config import Constant
#---------------------------------------------------
import random, time, json
#===================================================


class Bot(object):

    def __init__(self):
        self.emoticons = Constant.EMOTICON
        self.gifs = []
        self.last_time = time.time()
    
    def time_schedule(self):
        r = ''
        now = time.time()
        if int(now - self.last_time) > 3600:
            self.last_time = now
            url_latest = Constant.BOT_ZHIHU_URL_LATEST
            url_daily = Constant.BOT_ZHIHU_URL_DAILY
            data = get(url_latest)
            j = json.loads(data)
            story = j['stories'][random.randint(0, len(j['stories'])-1)]
            r = story['title'] + '\n' + url_daily + str(story['id'])
        return r.encode('utf-8')

    def reply(self, text):
        APIKEY = Constant.BOT_TULING_API_KEY
        api_url = Constant.BOT_TULING_API_URL % (APIKEY, text, '12345678')
        r = json.loads(get(api_url))
        if r.get('code') == 100000 and r.get('text') != Constant.BOT_TULING_BOT_REPLY:
            p = random.randint(1, 10)
            if p > 3:
                return r['text']
            elif p > 1:
                # send emoji
                if random.randint(1, 10) > 5:
                    n = random.randint(0, len(self.emoticons)-1)
                    m = random.randint(1, 3)
                    reply = self.emoticons[n].encode('utf-8') * m
                    return reply
        return ''
