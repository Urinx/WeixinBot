#!/usr/bin/env python
# coding: utf-8

#===================================================
from config import Log
from config import Constant
#---------------------------------------------------
import qrcode
import re
import os
import sys
import json
import urllib
import urllib2
import cookielib
import cPickle as pickle
import traceback
import time
import hashlib
#===================================================


def _decode_data(data):
    """
    @brief      decode array or dict to utf-8
    @param      data   array or dict
    @return     utf-8
    """
    if isinstance(data, dict):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            rv[key] = _decode_data(value)
        return rv
    elif isinstance(data, list):
        rv = []
        for item in data:
            item = _decode_data(item)
            rv.append(item)
        return rv
    elif isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data


def str2qr_terminal(text):
    """
    @brief      convert string to qrcode matrix and outprint
    @param      text   The string
    """
    Log.debug(text)
    qr = qrcode.QRCode()
    qr.border = 1
    qr.add_data(text)
    mat = qr.get_matrix()
    print_qr(mat)


def str2qr_image(text, image_path):
    """
    @brief      convert string to qrcode image & save
    @param      text         The string
    @param      image_path   Save image to the path
    """
    qr = qrcode.QRCode()
    qr.border = 1
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(image_path)


def print_qr(mat):
    for i in mat:
        BLACK = Constant.QRCODE_BLACK
        WHITE = Constant.QRCODE_WHITE
        echo(''.join([BLACK if j else WHITE for j in i])+'\n')


def echo(str):
    Log.info(str[:-1])
    sys.stdout.write(str)
    sys.stdout.flush()


def run(str, func, *args):
    t = time.time()
    echo(str)
    r = False
    try:
        r = func(*args)
    except:
        Log.error(traceback.format_exc())
    if r:
        totalTime = int(time.time() - t)
        echo(Constant.RUN_RESULT_SUCCESS % totalTime)
    else:
        echo(Constant.RUN_RESULT_FAIL)
        exit()


def get(url, api=None):
    """
    @brief      http get request
    @param      url   String
    @param      api   wechat api
    @return     http response
    """
    Log.debug('GET -> ' + url)
    request = urllib2.Request(url=url)
    request.add_header(*Constant.HTTP_HEADER_CONNECTION)
    request.add_header(*Constant.HTTP_HEADER_REFERER)
    if api in ['webwxgetvoice', 'webwxgetvideo']:
        request.add_header(*Constant.HTTP_HEADER_RANGE)

    while True:
        try:
            response = urllib2.urlopen(request, timeout=30)
            data = response.read()
            response.close()
            if api == None:
                Log.debug(data)
            return data
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            Log.error(traceback.format_exc())

        time.sleep(1)


def post(url, params, jsonfmt=True):
    """
    @brief      http post request
    @param      url      String
    @param      params   Dict, post params
    @param      jsonfmt  Bool, whether is json format
    @return     http response
    """
    Log.debug('POST -> '+url)
    Log.debug(params)
    if jsonfmt:
        request = urllib2.Request(url=url, data=json.dumps(params, ensure_ascii=False).encode('utf8'))
        request.add_header(*Constant.HTTP_HEADER_CONTENTTYPE)
    else:
        request = urllib2.Request(url=url, data=urllib.urlencode(params))

    while True:
        try:
            response = urllib2.urlopen(request, timeout=30)
            data = response.read()
            response.close()

            if jsonfmt:
                Log.debug(data)
                return json.loads(data, object_hook=_decode_data)
            return data
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            Log.error(traceback.format_exc())

        time.sleep(1)


def set_cookie(cookie_file):
    """
    @brief      Load cookie from file
    @param      cookie_file
    @param      user_agent
    @return     cookie, LWPCookieJar
    """
    cookie = cookielib.LWPCookieJar(cookie_file)
    try:
        cookie.load(ignore_discard=True)
    except:
        Log.error(traceback.format_exc())
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    opener.addheaders = Constant.HTTP_HEADER_USERAGENT
    urllib2.install_opener(opener)
    return cookie


def generate_file_name(filename):
    """
    @brief      generate file name
    @return     new file name
    """
    i = filename.rfind('.')
    ext = filename[i:]
    tmp = filename + str(int(time.time()))
    hash_md5 = hashlib.md5(tmp)
    return hash_md5.hexdigest() + ext


def save_file(filename, data, dirName):
    """
    @brief      Saves raw data to file.
    @param      filename  String
    @param      data      Binary data
    @param      dirName   String
    @return     file path
    """
    Log.debug('save file: ' + filename)
    fn = filename
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    fn = os.path.join(dirName, filename)
    with open(fn, 'wb') as f:
        f.write(data)
    return fn


def save_json(filename, data, dirName, mode='w+'):
    """
    @brief      Saves dict to json file.
    @param      filename  String
    @param      data      Dict
    @param      dirName   String
    @return     file path
    """
    Log.debug('save json: ' + filename)
    fn = filename
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    fn = os.path.join(dirName, filename)
    with open(fn, mode) as f:
        f.write(json.dumps(data, indent=4)+'\n')
    return fn


def load_json(filepath):
    Log.debug('load json: ' + filepath)
    with open(filepath, 'r') as f:
        return _decode_data(json.loads(f.read()))


def pickle_save(data, file):
    """
    @brief      Use pickle to save python object into file
    @param      data  The pyhton data
    @param      file  The file
    """
    basedir = os.path.dirname(file)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(file, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def pickle_load(file):
    """
    @brief      Use pickle to load python object from file
    @param      file  The file
    @return     python data
    """
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            return pickle.load(f)
    return None


def search_content(key, content, fmat='attr'):
    """
    @brief      Search content from xml or html format
    @param      key      String
    @param      content  String
    @param      fmat     attr
                         xml
    @return     String
    """
    if fmat == 'attr':
        pm = re.search(key + '\s?=\s?"([^"<]+)"', content)
        if pm:
            return pm.group(1)
    elif fmat == 'xml':
        pm = re.search('<{0}>([^<]+)</{0}>'.format(key), content)
        if not pm:
            pm = re.search(
                '<{0}><\!\[CDATA\[(.*?)\]\]></{0}>'.format(key), content)
        if pm:
            return pm.group(1)
    return 'unknown'


def is_str(s):
    """
    @brief      Determines if string.
    @param      s     String
    @return     True if string, False otherwise.
    """
    return isinstance(s, basestring)


def trans_coding(data):
    """
    @brief      Transform string to unicode
    @param      data  String
    @return     unicode
    """
    if not data:
        return data
    result = None
    if type(data) == unicode:
        result = data
    elif type(data) == str:
        result = data.decode('utf-8')
    return result


def trans_emoji(text):
    """
    @brief      Transform emoji html text to unicode
    @param      text  String
    @return     emoji unicode
    """
    def _emoji(matched):
        hex = matched.group(1)
        return ('\\U%08x' % int(hex, 16)).decode('unicode-escape').encode('utf-8')

    replace_t = re.sub(Constant.REGEX_EMOJI, _emoji, text)
    return replace_t


def auto_reload(mod):
    """
    @brief      reload modules
    @param      mod: the need reload modules
    """
    try:
        module = sys.modules[mod]
    except:
        Log.error(traceback.format_exc())
        return False

    filename = module.__file__
    # .pyc 修改时间不会变
    # 所以就用 .py 的修改时间
    if filename.endswith(".pyc"):
        filename = filename.replace(".pyc", ".py")
    mod_time = os.path.getmtime(filename)
    if not "loadtime" in module.__dict__:
        module.loadtime = 0

    try:
        if mod_time > module.loadtime:
            reload(module)
        else:
            return False
    except:
        Log.error(traceback.format_exc())
        return False

    module.loadtime = mod_time

    echo('[*] load \'%s\' successful.\n' % mod)
    return True


def split_array(arr, n):
    for i in xrange(0, len(arr), n):
        yield arr[i:i+n]

