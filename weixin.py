#!/usr/bin/env python
# coding: utf-8
import qrcode
import urllib, urllib2
import cookielib
import requests
import xml.dom.minidom
import json
import time, re, sys, os, random
import multiprocessing
import platform
from collections import defaultdict

def catchKeyboardInterrupt(fn):
	def wrapper(*args):
		try:
			return fn(*args)
		except KeyboardInterrupt:
			print '\n[*] 强制退出程序'
	return wrapper

def _decode_list(data):
	rv = []
	for item in data:
		if isinstance(item, unicode):
			item = item.encode('utf-8')
		elif isinstance(item, list):
			item = _decode_list(item)
		elif isinstance(item, dict):
			item = _decode_dict(item)
		rv.append(item)
	return rv

def _decode_dict(data):
	rv = {}
	for key, value in data.iteritems():
		if isinstance(key, unicode):
			key = key.encode('utf-8')
		if isinstance(value, unicode):
			value = value.encode('utf-8')
		elif isinstance(value, list):
			value = _decode_list(value)
		elif isinstance(value, dict):
			value = _decode_dict(value)
		rv[key] = value
	return rv

class WebWeixin(object):
	def __str__(self):
		description = \
		"=========================\n" + \
		"[#] Web Weixin\n" + \
		"[#] Debug Mode: " + str(self.DEBUG) + "\n" + \
		"[#] Uuid: " + self.uuid + "\n" + \
		"[#] Uin: " + str(self.uin) + "\n" + \
		"[#] Sid: " + self.sid + "\n" + \
		"[#] Skey: " + self.skey + "\n" + \
		"[#] DeviceId: " + self.deviceId + "\n" + \
		"[#] PassTicket: " + self.pass_ticket + "\n" + \
		"========================="
		return description

	def __init__(self):
		self.DEBUG = False
		self.uuid = ''
		self.base_uri = ''
		self.redirect_uri= ''
		self.uin = ''
		self.sid = ''
		self.skey = ''
		self.pass_ticket = ''
		self.deviceId = 'e' + repr(random.random())[2:17]
		self.BaseRequest = {}
		self.synckey = ''
		self.SyncKey = []
		self.User = []
		self.MemberList = []
		self.ContactList = []
		self.GroupList = []
		self.autoReplyMode = False
		self.syncHost = ''

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
		urllib2.install_opener(opener)

	def getUUID(self):
		url = 'https://login.weixin.qq.com/jslogin'
		params = {
			'appid': 'wx782c26e4c19acffb',
			'fun': 'new',
			'lang': 'zh_CN',
			'_': int(time.time()),
		}
		data = self._post(url, params, False)
		regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
		pm = re.search(regx, data)
		if pm:
			code = pm.group(1)
			self.uuid = pm.group(2)
			return code == '200'
		return False

	def genQRCode(self):
		if sys.platform.find('win') >= 0:
			self._showQRCodeImg()
		else:
			self._str2qr('https://login.weixin.qq.com/l/' + self.uuid)

	def _showQRCodeImg(self):
		QRCODE_PATH = os.path.join(os.getcwd(),'qrcode.jpg')
		url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
		params = {
			't' : 'webwx',
			'_' : int(time.time())
		}

		data = self._post(url,params,False)
		with open(QRCODE_PATH, 'wb') as f:
			f.write(data)

		os.startfile(QRCODE_PATH)

	def waitForLogin(self, tip = 1):
		time.sleep(tip)
		url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, self.uuid, int(time.time()))
		data = self._get(url)
		pm = re.search(r'window.code=(\d+);', data)
		code = pm.group(1)

		if code == '201': return True
		elif code == '200':
			pm = re.search(r'window.redirect_uri="(\S+?)";', data)
			r_uri = pm.group(1) + '&fun=new'
			self.redirect_uri = r_uri
			self.base_uri = r_uri[:r_uri.rfind('/')]
			return True
		elif code == '408':
			self._echo('[登陆超时] ')
		else:
			self._echo('[登陆异常] ')
		return False

	def login(self):
		data = self._get(self.redirect_uri)
		doc = xml.dom.minidom.parseString(data)
		root = doc.documentElement

		for node in root.childNodes:
			if node.nodeName == 'skey':
				self.skey = node.childNodes[0].data
			elif node.nodeName == 'wxsid':
				self.sid = node.childNodes[0].data
			elif node.nodeName == 'wxuin':
				self.uin = node.childNodes[0].data
			elif node.nodeName == 'pass_ticket':
				self.pass_ticket = node.childNodes[0].data

		if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
			return False

		self.BaseRequest = {
			'Uin': int(self.uin),
			'Sid': self.sid,
			'Skey': self.skey,
			'DeviceID': self.deviceId,
		}
		return True

	def webwxinit(self):
		url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (self.pass_ticket, self.skey, int(time.time()))
		params = {
			'BaseRequest': self.BaseRequest
		}
		dic = self._post(url, params)
		self.SyncKey = dic['SyncKey']
		self.User = dic['User']
		# synckey for synccheck
		self.synckey = '|'.join([ str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List'] ])

		return dic['BaseResponse']['Ret'] == 0

	def webwxstatusnotify(self):
		url = self.base_uri + '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
		params = {
			'BaseRequest': self.BaseRequest,
			"Code": 3,
			"FromUserName": self.User['UserName'],
			"ToUserName": self.User['UserName'],
			"ClientMsgId": int(time.time())
		}
		dic = self._post(url, params)

		return dic['BaseResponse']['Ret'] == 0

	def webwxgetcontact(self):
		url = self.base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (self.pass_ticket, self.skey, int(time.time()))
		dic = self._post(url, {})
		self.MemberList = dic['MemberList']

		ContactList = self.MemberList[:]
		SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
		for i in xrange(len(ContactList) - 1, -1, -1):
			Contact = ContactList[i]
			if Contact['VerifyFlag'] & 8 != 0: # 公众号/服务号
				ContactList.remove(Contact)
			elif Contact['UserName'] in SpecialUsers: # 特殊账号
				ContactList.remove(Contact)
			elif Contact['UserName'].find('@@') != -1: # 群聊
				self.GroupList.append(Contact)
				ContactList.remove(Contact)
			elif Contact['UserName'] == self.User['UserName']: # 自己
				ContactList.remove(Contact)
		self.ContactList = ContactList

		return True

	def webwxbatchgetcontact(self):
		url = self.base_uri + '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (int(time.time()), self.pass_ticket)
		params = {
			'BaseRequest': self.BaseRequest,
			"Count": len(self.GroupList),
			"List": [ {"UserName": g['UserName'], "EncryChatRoomId":""} for g in self.GroupList ]
		}
		dic = self._post(url, params)
		# blabla ...
		return True

	def testsynccheck(self):
		SyncHost = [
			'webpush.weixin.qq.com',
			'webpush2.weixin.qq.com',
			'webpush.wechat.com',
			'webpush1.wechat.com',
			'webpush2.wechat.com',
			'webpush1.wechatapp.com',
			# 'webpush.wechatapp.com'
		]
		for host in SyncHost:
			self.syncHost = host
			[retcode, selector] = self.synccheck()
			if retcode == '0': return True
		return False

	def synccheck(self):
		params = {
			'r': int(time.time()),
			'sid': self.sid,
			'uin': self.uin,
			'skey': self.skey,
			'deviceid': self.deviceId,
			'synckey': self.synckey,
			'_': int(time.time()),
		}
		url = 'https://' + self.syncHost + '/cgi-bin/mmwebwx-bin/synccheck?' + urllib.urlencode(params)
		data = self._get(url)
		pm = re.search(r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
		retcode = pm.group(1)
		selector = pm.group(2)
		return [retcode, selector]

	def webwxsync(self):
		url = self.base_uri + '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (self.sid, self.skey, self.pass_ticket)
		params = {
			'BaseRequest': self.BaseRequest,
			'SyncKey': self.SyncKey,
			'rr': ~int(time.time())
		}
		dic = self._post(url, params)
		if self.DEBUG:
			print json.dumps(dic, indent=4)

		if dic['BaseResponse']['Ret'] == 0:
			self.SyncKey = dic['SyncKey']
			self.synckey = '|'.join([ str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List'] ])
		return dic

	def webwxsendmsg(self, word, to = 'filehelper'):
		url = self.base_uri + '/webwxsendmsg?pass_ticket=%s' % (self.pass_ticket)
		clientMsgId = str(int(time.time()*1000)) + str(random.random())[:5].replace('.','')
		params = {
			'BaseRequest': self.BaseRequest,
			'Msg': {
				"Type": 1,
				"Content": self._transcoding(word),
				"FromUserName": self.User['UserName'],
				"ToUserName": to,
				"LocalID": clientMsgId,
				"ClientMsgId": clientMsgId
			}
		}
		headers = {'content-type': 'application/json; charset=UTF-8'}
		data = json.dumps(params, ensure_ascii=False).encode('utf8')
		r = requests.post(url, data = data, headers = headers)
		dic = r.json()
		return dic['BaseResponse']['Ret'] == 0

	def webwxgeticon(self, id):
		url = self.base_uri + '/webwxgeticon?username=%s&skey=%s' % (id, self.skey)
		data = self._get(url)
		fn = 'img_'+id+'.jpg'
		with open(fn, 'wb') as f: f.write(data)
		return fn

	def webwxgetheadimg(self, id):
		url = self.base_uri + '/webwxgetheadimg?username=%s&skey=%s' % (id, self.skey)
		data = self._get(url)
		fn = 'img_'+id+'.jpg'
		with open(fn, 'wb') as f: f.write(data)
		return fn

	def webwxgetmsgimg(self, msgid):
		url = self.base_uri + '/webwxgetmsgimg?MsgID=%s&skey=%s' % (msgid, self.skey)
		data = self._get(url)
		fn = 'img_'+msgid+'.jpg'
		with open(fn, 'wb') as f: f.write(data)
		return fn

	# Not work now for weixin haven't support this API
	def webwxgetvideo(self, msgid):
		url = self.base_uri + '/webwxgetvideo?msgid=%s&skey=%s' % (msgid, self.skey)
		data = self._get(url)
		fn = 'video_'+msgid+'.mp4'
		with open(fn, 'wb') as f: f.write(data)
		return fn

	def webwxgetvoice(self, msgid):
		url = self.base_uri + '/webwxgetvoice?msgid=%s&skey=%s' % (msgid, self.skey)
		data = self._get(url)
		fn = 'voice_'+msgid+'.mp3'
		with open(fn, 'wb') as f: f.write(data)
		return fn

	def getUserRemarkName(self, id):
		name = '未知群' if id[:2] == '@@' else '陌生人'
		if id == self.User['UserName']: return self.User['NickName']
		for member in self.MemberList:
			if member['UserName'] == id:
				name = member['RemarkName'] if member['RemarkName'] else member['NickName']
		return name

	def getUSerID(self, name):
		for member in self.MemberList:
			if name == member['RemarkName'] or name == member['NickName']:
				return member['UserName']
		return None

	def handleMsg(self, r):
		for msg in r['AddMsgList']:
			print '[*] 你有新的消息，请注意查收'

			if self.DEBUG:
				fn = 'msg' + str(int(random.random() * 1000)) + '.json'
				with open(fn, 'w') as f: f.write(json.dumps(msg))
				print '[*] 该消息已储存到文件: ' + fn

			msgType = msg['MsgType']
			name = self.getUserRemarkName(msg['FromUserName'])
			content = msg['Content'].replace('&lt;','<').replace('&gt;','>')
			msgid = msg['MsgId']
			if msgType == 51:
				print '[*] 成功截获微信初始化消息'
			elif msgType == 1:
				if content.find('http://weixin.qq.com/cgi-bin/redirectforward?args=') != -1:
					# 地理位置消息
					data = self._get(content).decode('gbk').encode('utf-8')
					pos = self._searchContent('title', data, 'xml')
					print '%s 给你发送了一个位置消息 [我在%s]' % (name, pos)
				elif msg['ToUserName'] == 'filehelper':
					print '%s -> 文件传输助手: %s' % (name, content.replace('<br/>','\n'))
				elif msg['FromUserName'] == self.User['UserName']:
					pass
				elif msg['FromUserName'][:2] == '@@':
					[people, content] = content.split(':<br/>')
					group = self.getUserRemarkName(msg['FromUserName'])
					name = self.getUserRemarkName(people)
					print '|%s| %s: %s' % (group, name, content.replace('<br/>','\n'))
				else:
					print name+': '+content
					if self.autoReplyMode:
						ans = self._xiaodoubi(content)+'\n[微信机器人自动回复]'
						if self.webwxsendmsg(ans, msg['FromUserName']):
							print '自动回复: '+ans
						else:
							print '自动回复失败'
			elif msgType == 3:
				image = self.webwxgetmsgimg(msgid)
				print '%s 给你发送了一张图片: %s' % (name, image)
				self._safe_open(image)
			elif msgType == 34:
				voice = self.webwxgetvoice(msgid)
				print '%s 给你发了一段语音: %s' % (name, voice)
				self._safe_open(voice)
			elif msgType == 42:
				info = msg['RecommendInfo']
				print '%s 给你发送了一张名片:' % name
				print '========================='
				print '= 昵称: %s' % info['NickName']
				print '= 微信号: %s' % info['Alias']
				print '= 地区: %s %s' % (info['Province'], info['City'])
				print '= 性别: %s' % ['未知', '男', '女'][info['Sex']]
				print '========================='
			elif msgType == 47:
				url = self._searchContent('cdnurl', content)
				print '%s 给你发了一个动画表情，点击下面链接查看:\n%s' % (name, url)
				self._safe_open(url)
			elif msgType == 49:
				appMsgType = defaultdict(lambda : "")
				appMsgType.update({5:'链接', 3:'音乐', 7:'微博'})
				print '%s 给你分享了一个%s:' % (name, appMsgType[msg['AppMsgType']])
				print '========================='
				print '= 标题: %s' % msg['FileName']
				print '= 描述: %s' % self._searchContent('des', content, 'xml')
				print '= 链接: %s' % msg['Url']
				print '= 来自: %s' % self._searchContent('appname', content, 'xml')
				print '========================='
			elif msgType == 62:
				print name+' 给你发了一个小视频，请在手机上查看'
			elif msgType == 10002:
				print name+' 撤回消息'
			else:
				print '[*] 该消息类型为: %d，可能是表情，图片或链接' % msg['MsgType']
				print msg

	def listenMsgMode(self):
		print '[*] 进入消息监听模式 ... 成功'
		self._run('[*] 进行同步线路测试 ... ', self.testsynccheck)
		playWeChat = 0
		while True:
			[retcode, selector] = self.synccheck()
			if self.DEBUG: print 'retcode: %s, selector: %s' % (retcode, selector)
			if retcode == '1100':
				print '[*] 你在手机上登出了微信，债见'
				break
			elif retcode == '0':
				if selector == '2':
					r = self.webwxsync()
					if r is not None: self.handleMsg(r)
				elif selector == '7':
					playWeChat += 1
					print '[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat
					r = self.webwxsync()
				elif selector == '0':
					time.sleep(1)

	def sendMsg(self, name, word, isfile = False):
		id = self.getUSerID(name)
		if id:
			if isfile:
				with open(word, 'r') as f:
					for line in f.readlines():
						line = line.replace('\n','')
						self._echo('-> '+name+': '+line)
						if self.webwxsendmsg(line, id):
							print ' [成功]'
						else:
							print ' [失败]'
						time.sleep(1)
			else:
				if self.webwxsendmsg(word, id):
					print '[*] 消息发送成功'
				else:
					print '[*] 消息发送失败'
		else:
			print '[*] 此用户不存在'

	def sendMsgToAll(self, word):
		for contact in self.ContactList:
			name = contact['RemarkName'] if contact['RemarkName'] else contact['NickName']
			id = contact['UserName']
			self._echo('-> '+name+': '+word)
			if self.webwxsendmsg(word, id):
				print ' [成功]'
			else:
				print ' [失败]'
			time.sleep(1)

	@catchKeyboardInterrupt
	def start(self):
		print '[*] 微信网页版 ... 开动'
		self._run('[*] 正在获取 uuid ... ', self.getUUID)
		print '[*] 正在获取二维码 ... 成功'; self.genQRCode()
		self._run('[*] 请使用微信扫描二维码以登录 ... ', self.waitForLogin)
		self._run('[*] 请在手机上点击确认以登录 ... ', self.waitForLogin, 0)
		self._run('[*] 正在登录 ... ', self.login)
		self._run('[*] 微信初始化 ... ', self.webwxinit)
		self._run('[*] 开启状态通知 ... ', self.webwxstatusnotify)
		self._run('[*] 获取联系人 ... ', self.webwxgetcontact)
		print '[*] 共有 %d 位联系人' % len(self.ContactList)
		if self.DEBUG: print self

		if raw_input('[*] 是否开启自动回复模式(y/n): ') == 'y':
			self.autoReplyMode = True
			print '[*] 自动回复模式 ... 开启'
		else:
			print '[*] 自动回复模式 ... 关闭'

		listenProcess = multiprocessing.Process(target=self.listenMsgMode)
		listenProcess.start()

		while True:
			text = raw_input('')
			if text == 'quit':
				listenProcess.terminate()
				print('[*] 退出微信')
				exit()
			elif text[:2] == '->':
				[name, word] = text[2:].split(':')
				if name == 'all': self.sendMsgToAll(word)
				else: self.sendMsg(name, word)
			elif text[:3] == 'm->':
				[name, file] = text[3:].split(':')
				self.sendMsg(name, file, True)
			elif text[:3] == 'f->':
				print '发送文件'
			elif text[:3] == 'i->':
				print '发送图片'

	def _safe_open(self, path):
		if platform.system() == "Linux":
		    os.system("xdg-open %s &" % path)
		else:
			os.system('open %s &' % path)

	def _run(self, str, func, *args):
		self._echo(str)
		if func(*args): print '成功'
		else: print('失败\n[*] 退出程序');exit()

	def _echo(self, str):
		sys.stdout.write(str)
		sys.stdout.flush()

	def _printQR(self, mat):
		for i in mat:
			BLACK = '\033[40m  \033[0m'
			WHITE = '\033[47m  \033[0m'
			print ''.join([BLACK if j else WHITE for j in i])

	def _str2qr(self, str):
		qr = qrcode.QRCode()
		qr.border = 1
		qr.add_data(str)
		mat = qr.get_matrix()
		self._printQR(mat) # qr.print_tty() or qr.print_ascii()

	def _transcoding(self, data):
		if not data: return data
		result = None
		if type(data) == unicode:
			result = data
		elif type(data) == str:
			result = data.decode('utf-8')
		return result

	def _get(self, url):
		request = urllib2.Request(url = url)
		response = urllib2.urlopen(request)
		data = response.read()
		return data

	def _post(self, url, params, jsonfmt = True):
		if jsonfmt:
			request = urllib2.Request(url = url, data = json.dumps(params))
			request.add_header('ContentType', 'application/json; charset=UTF-8')
		else:
			request = urllib2.Request(url = url, data = urllib.urlencode(params))
		response = urllib2.urlopen(request)
		data = response.read()
		if jsonfmt: return json.loads(data, object_hook=_decode_dict)
		return data

	def _xiaodoubi(self, word):
		url = 'http://www.xiaodoubi.com/bot/chat.php'
		try:
			r = requests.post(url, data = {'chat': word})
			return r.content
		except:
			return "让我一个人静静 T_T..."

	def _simsimi(self, word):
		key = ''
		url = 'http://sandbox.api.simsimi.com/request.p?key=%s&lc=ch&ft=0.0&text=%s' % (key, word)
		r = requests.get(url)
		ans = r.json()
		if ans['result'] == '100': return ans['response']
		else: return '你在说什么，风太大听不清列'

	def _searchContent(self, key, content, fmat = 'attr'):
		if fmat == 'attr':
			pm = re.search(key+'\s?=\s?"([^"<]+)"', content)
			if pm: return pm.group(1)
		elif fmat == 'xml':
			pm=re.search('<{0}>([^<]+)</{0}>'.format(key),content)
			if pm: return pm.group(1)
		return '未知'

class UnicodeStreamFilter:
	def __init__(self, target):
		self.target = target
		self.encoding = 'utf-8'
		self.errors = 'replace'
		self.encode_to = self.target.encoding

	def write(self, s):
		if type(s) == str:
			s = s.decode('utf-8')
		s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
		self.target.write(s)

	def flush(self):
		self.target.flush()

if sys.stdout.encoding == 'cp936':
	sys.stdout = UnicodeStreamFilter(sys.stdout)


if __name__ == '__main__':
	webwx = WebWeixin()
	webwx.start()
