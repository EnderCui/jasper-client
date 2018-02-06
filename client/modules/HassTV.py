# -*- coding: utf-8-*-
import sys
import time
import json
import logging
from requests import post

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["HOMEASSISTANT"]
SLUG = "home_assistant"

PHRASES = [u"打开", u"关闭", u"我想看", u"遥控"]
OPERATION = {
    u"电视": 'switch.tv',
    u"主页": 'switch.tv_homepage',
    u"上边": 'switch.tv_up',
    u"下边": 'switch.tv_down',
    u"左边": 'switch.tv_left',
    u"右边": 'switch.tv_right',
    u"确定": 'switch.tv_confirm',
    u"后退": 'switch.tv_backward',
    u"大点声": 'switch.tv_volup',
    u"小点声": 'switch.tv_voldown',
    u"儿歌": 'switch.song',
    u"直播": 'switch.live'}

LOGGER = logging.getLogger(__name__)


def isValid(text):
    for phrases in PHRASES:
        if text.startswith(phrases):
            return True
    return False


def handle(text, mic, profile, bot=None):
    '''
    home_assistant:
        Host: "192.168.2.235"
        Port: "8123"
        Password: "password"
    '''
    if SLUG not in profile or \
       'Host' not in profile[SLUG] or \
       'Port' not in profile[SLUG] or \
       'Password' not in profile[SLUG]:
        mic.say(u"插件配置有误，插件使用失败")
        return

    host = profile[SLUG]['Host']
    port = profile[SLUG]['Port'] if 'Port' in profile[SLUG] else 8123
    password = profile[SLUG]['Password']

    url = 'http://' + host + ':' + str(port) + '/api/services/'
    headers = {'x-ha-access': password, 'content-type': 'application/json'}
    text = text.strip().replace("，", "").replace("。", "")
    key = text.decode('utf-8')[2:]
    cmd = "turn_off" if text.decode('utf-8')[:2] == u"关闭" else "turn_on"

    if key in OPERATION:
        service = 'switch'
        requestService = url + service + "/" + cmd
        if key == u"儿歌": watchSong(requestService, headers, mic)
        if key == u"直播": watchLive(requestService, headers, mic)
        if key == u"主页": watchHomepage(requestService, headers, mic)
        if key == u"电视": operateTv(requestService, headers, mic, key)
        if key == u"上边": operateTv(requestService, headers, mic, key)
        if key == u"下边": operateTv(requestService, headers, mic, key)
        if key == u"左边": operateTv(requestService, headers, mic, key)
        if key == u"右边": operateTv(requestService, headers, mic, key)
        if key == u"大点声": operateTv(requestService, headers, mic, key)
        if key == u"小点声": operateTv(requestService, headers, mic, key)
    else:
        mic.say(u"我没办法完成" + text + u"操作")


def watchSong(requestService, headers, mic):
    try:
        data = json.dumps({'entity_id': OPERATION[u"下边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"右边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
        time.sleep(10)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
        time.sleep(20)

        data = json.dumps({'entity_id': OPERATION[u"上边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"上边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"右边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"右边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
        time.sleep(4)

        data = json.dumps({'entity_id': OPERATION[u"下边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"下边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
    except Exception as e:
        mic.say(u"不能遥控打开儿歌")
        LOGGER.error(e)


def watchLive(requestService, headers, mic):
    try:
        data = json.dumps({'entity_id': OPERATION[u"下边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"右边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
        time.sleep(10)

        data = json.dumps({'entity_id': OPERATION[u"右边"]})
        response = post(requestService, data, headers=headers)
        time.sleep(1)

        data = json.dumps({'entity_id': OPERATION[u"确定"]})
        response = post(requestService, data, headers=headers)
    except Exception as e:
        mic.say(u"不能遥控打开直播")
        LOGGER.error(e)


def watchHomepage(requestService, headers, mic):
    try:
        data = json.dumps({'entity_id': OPERATION[u"后退"]})
        response = post(requestService, data, headers=headers)
        time.sleep(2)

        data = json.dumps({'entity_id': OPERATION[u"后退"]})
        response = post(requestService, data, headers=headers)
        time.sleep(2)

        data = json.dumps({'entity_id': OPERATION[u"后退"]})
        response = post(requestService, data, headers=headers)
        time.sleep(2)

        data = json.dumps({'entity_id': OPERATION[u"主页"]})
        response = post(requestService, data, headers=headers)
    except Exception as e:
        mic.say(u"不能遥控打开主页")
        LOGGER.error(e)


def operateTv(requestService, headers, mic, key):
    try:
        data = json.dumps({'entity_id': OPERATION[key]})
        response = post(requestService, data, headers=headers)
    except Exception as e:
        mic.say(u"抱歉，无法遥控电视")
        LOGGER.error(e)
