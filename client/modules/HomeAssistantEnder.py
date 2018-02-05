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

PHRASES = [u"打开", u"关闭"]

GROUP = [u"儿歌", u"直播"]

DEVICES = {u"电视": 'switch.tv',
           u"左边": 'switch.tvleft',
           u"右边": 'switch.tvright',
           u"下边": 'switch.tvdown',
           u"上边": 'switch.tvup',
           u"确定": 'switch.tvconfirm',
           u"后退": 'switch.tvbackward',
           u"儿歌": 'switch.song',
           u"直播": 'switch.bo',
           u"空调": 'switch.ac',
           u"盒子": 'switch.damai_box_power',
           u"灯": 'switch.panasonic_light_power'}


def handle(text, mic, profile, bot=None):
    logger = logging.getLogger(__name__)
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
    cmd = "turn_on" if text.decode('utf-8')[:2] == u"打开" else "turn_off"

    if key in DEVICES:
       # data = json.dumps({'entity_id': DEVICES[key]})
        if key in GROUP:
             try:
                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 service = DEVICES[u"下边"].split('.')[0]
                 # service = "tvdown"
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(2)
                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 service = DEVICES[u"右边"].split('.')[0]
                 # service = 'tvright'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(2)
                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 service = DEVICES[u"确定"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(15)
                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 service = DEVICES[u"确定"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(20)
                 data = json.dumps({'entity_id': DEVICES[u"上边"]})
                 service = DEVICES[u"上边"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"上边"]})
                 service = DEVICES[u"上边"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 service = DEVICES[u"右边"].split('.')[0]
                 # service = 'tvright'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 service = DEVICES[u"右边"].split('.')[0]
                 # service = 'tvright'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 service = DEVICES[u"确定"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(3)
                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 service = DEVICES[u"下边"].split('.')[0]
                 # service = 'tvright'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 service = DEVICES[u"下边"].split('.')[0]
                 # service = 'tvright'
                 response = post(url + service + "/" + cmd, data, headers=headers)

                 time.sleep(1)
                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 service = DEVICES[u"确定"].split('.')[0]
                 # service = 'tvconfirm'
                 response = post(url + service + "/" + cmd, data, headers=headers)

             except Exception as ex:
                 mic.say(u"不能" + text)
                 logger.error(ex)
        else:
             try:
                 data = json.dumps({'entity_id': DEVICES[key]})
                 service = DEVICES[key].split('.')[0]
                 response = post(url + service + "/" + cmd, data, headers=headers)
                 logger.debug(response)
                 mic.say(text)
             except Exception as e:
                 mic.say(u"无法" + text)
                 logger.error(e)
    else:
        mic.say(u"无法匹配")


def isValid(text):
    for phrases in PHRASES:
        if text.startswith(phrases):
            return True
    return False
