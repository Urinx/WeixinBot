#!/usr/bin/env python
# coding: utf-8

#===================================================
from wechat import WeChat
from wechat.utils import *
from wx_handler import WeChatMsgProcessor
from wx_handler import Bot
from wx_handler import SGMail
from db import SqliteDB
from db import MysqlDB
from config import ConfigManager
from config import Constant
from config import Log
#---------------------------------------------------
from flask import Flask, render_template, send_file, jsonify, request
import threading
import traceback
import os
import logging
import time
#===================================================


cm = ConfigManager()
db = SqliteDB(cm.getpath('database'))
# db = MysqlDB(cm.mysql())
wechat_msg_processor = WeChatMsgProcessor(db)
wechat = WeChat(cm.get('wechat', 'host'))
wechat.db = db
wechat.bot = Bot()
wechat.msg_handler = wechat_msg_processor
wechat_msg_processor.wechat = wechat

PORT = int(cm.get('setting', 'server_port'))
app = Flask(__name__, template_folder='flask_templates')
app.config['UPLOAD_FOLDER'] = cm.getpath('uploaddir')

logger = logging.getLogger('werkzeug')
log_format_str = Constant.SERVER_LOG_FORMAT
formatter = logging.Formatter(log_format_str)
flask_log_handler = logging.FileHandler(cm.getpath('server_log_file'))
flask_log_handler.setLevel(logging.INFO)
flask_log_handler.setFormatter(formatter)
logger.addHandler(flask_log_handler)
app.logger.addHandler(flask_log_handler)

# sendgrid mail
sg_apikey = cm.get('sendgrid', 'api_key')
from_email = cm.get('sendgrid', 'from_email')
to_email = cm.get('sendgrid', 'to_email')
sg = SGMail(sg_apikey, from_email, to_email)

@app.route('/')
def index():
    return render_template(Constant.SERVER_PAGE_INDEX)


@app.route('/qrcode')
def qrcode():
    qdir = cm.getpath('qrcodedir')
    if not os.path.exists(qdir):
        os.makedirs(qdir)
    image_path = '%s/%s_%d.png' % (qdir, wechat.uuid, int(time.time()*100))
    s = wechat.wx_conf['API_qrcode'] + wechat.uuid
    str2qr_image(s, image_path)
    return send_file(image_path, mimetype='image/png')


@app.route("/group_list")
def group_list():
    """
    @brief      list groups
    """
    result = wechat.db.select(Constant.TABLE_GROUP_LIST())
    return jsonify({'count': len(result), 'group': result})


@app.route('/group_member_list/<g_id>')
def group_member_list(g_id):
    """
    @brief      list group member
    @param      g_id String
    """
    result = wechat.db.select(Constant.TABLE_GROUP_USER_LIST(), 'RoomID', g_id)
    return jsonify({'count': len(result), 'member': result})


@app.route('/group_chat_log/<g_name>')
def group_chat_log(g_name):
    """
    @brief      list group chat log
    @param      g_name String
    """
    result = wechat.db.select(Constant.TABLE_GROUP_MSG_LOG, 'RoomName', g_name)
    return jsonify({'count': len(result), 'chats': result})


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1] in Constant.SERVER_UPLOAD_ALLOWED_EXTENSIONS

        j = {'ret': 1, 'msg': ''}

        # check if the post request has the file part
        if 'file' not in request.files:
            j['msg'] = 'No file part'
            return jsonify(j)

        # if user does not select file, browser also
        # submit a empty part without filename
        file = request.files['file']
        if file.filename == '':
            j['msg'] = 'No selected file'
        elif file and allowed_file(file.filename):
            filename = generate_file_name(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            j['ret'] = 0
            j['msg'] = filename
        else:
            j['msg'] = 'File type not support'
        return jsonify(j)
    else:
        return render_template(Constant.SERVER_PAGE_UPLOAD)


@app.route('/send_msg/<to>/<msg>')
def send_msg(to, msg):
    """
    @brief      send message to user or gourp
    @param      to: String, user id or group id
    @param      msg: String, words
    """
    return jsonify({'ret': 0 if wechat.send_text(to, msg) else 1})


@app.route('/send_img/<to>/<img>')
def send_img(to, img):
    """
    @brief      send image to user or gourp
    @param      to: String, user id or group id
    @param      img: String, image file name
    """
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img)
    return jsonify({'ret': 0 if wechat.send_img(to, img_path) else 1})


@app.route('/send_emot/<to>/<emot>')
def send_emot(to, emot):
    """
    @brief      send emotion to user or gourp
    @param      to: String, user id or group id
    @param      emot: String, emotion file name
    """
    emot_path = os.path.join(app.config['UPLOAD_FOLDER'], emot)
    return jsonify({'ret': 0 if wechat.send_emot(to, emot_path) else 1})


@app.route('/send_file/<to>/<file>')
def send_file(to, file):
    """
    @brief      send file to user or gourp
    @param      to: String, user id or group id
    @param      file: String, file name
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    return jsonify({'ret': 0 if wechat.send_file(to, file_path) else 1})


def mass_send(method, data, func):
    j = {'ret': -1, 'unsend_list':[]}
    if method == 'POST' and data:
        to_list = data['to_list']
        msg = data['msg']
        media_type = data.get('media_type', '')

        if media_type in ['img', 'emot']:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], msg)
            response = wechat.webwxuploadmedia(file_path)
            if response is not None:
                msg = response['MediaId']
        elif media_type == 'file':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], msg)
            data = {
                'appid': Constant.API_WXAPPID,
                'title': msg,
                'totallen': '',
                'attachid': '',
                'type': wechat.wx_conf['APPMSGTYPE_ATTACH'],
                'fileext': msg.split('.')[-1],
            }
            response = wechat.webwxuploadmedia(file_path)
            if response is not None:
                data['totallen'] = response['StartPos']
                data['attachid'] = response['MediaId']
            else:
                Log.error('File upload error')
            msg = data

        for groups in split_array(to_list, 20):
            for g in groups:
                r = func(g, msg)
                if not r:
                    j['unsend_list'].append(g)
            time.sleep(1)

        j['ret'] = len(j['unsend_list'])

    return j


@app.route('/mass_send_msg/', methods=["GET", "POST"])
def mass_send_msg():
    """
    @brief      send text to mass users or gourps
    """
    j = mass_send(request.method, request.json, wechat.send_text)
    return jsonify(j)


@app.route('/mass_send_img', methods=["GET", "POST"])
def mass_send_img():
    """
    @brief      send iamge to mass users or gourps
    """
    j = mass_send(request.method, request.json, wechat.webwxsendmsgimg)
    return jsonify(j)


@app.route('/mass_send_emot', methods=["GET", "POST"])
def mass_send_emot():
    """
    @brief      send emoticon to mass users or gourps
    """
    j = mass_send(request.method, request.json, wechat.webwxsendemoticon)
    return jsonify(j)


@app.route('/mass_send_file', methods=["GET", "POST"])
def mass_send_file():
    """
    @brief      send file to mass users or gourps
    """
    j = mass_send(request.method, request.json, wechat.webwxsendappmsg)
    return jsonify(j)


def run_server():
    app.run(port=PORT)

if cm.get('setting', 'server_mode') == 'True':
    serverProcess = threading.Thread(target=run_server)
    serverProcess.start()

while True:
    try:
        wechat.start()
    except KeyboardInterrupt:
        echo(Constant.LOG_MSG_QUIT)
        wechat.exit_code = 1
    else:
        Log.error(traceback.format_exc())
    finally:
        wechat.stop()
    
    # send a mail to tell the wxbot is failing
    subject = 'wxbot stop message'
    log_file = open(eval(cm.get('handler_fileHandler', 'args'))[0], 'r')
    mail_content = '<pre>' + str(wechat) + '\n\n-----\nLogs:\n-----\n\n' + ''.join(log_file.readlines()[-100:]) + '</pre>'
    sg.send_mail(subject, mail_content, 'text/html')
    log_file.close()

    if wechat.exit_code == 0:
        echo(Constant.MAIN_RESTART)
    else:
        # kill process
        os.system(Constant.LOG_MSG_KILL_PROCESS % os.getpid())
