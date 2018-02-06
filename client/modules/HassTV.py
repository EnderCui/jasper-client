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

PHRASES = [u"我想看", u"遥控", u"关闭"]
DEVICES = {u"电视": 'switch.tv',
           u"主页": 'switch.tv_homepage',
           u"左边": 'switch.tv_left',
           u"右边": 'switch.tv_right',
           u"下边": 'switch.tv_down',
           u"上边": 'switch.tv_up',
           u"确定": 'switch.tv_confirm',
           u"后退": 'switch.tv_backward',
           u"大点声": 'switch.tv_volup',
           u"小点声": 'switch.tv_voldown',
           u"儿歌": 'switch.song',
           u"直播": 'switch.bo'}

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
    #cmd = "turn_on" if text.decode('utf-8')[:2] == u"打开" else "turn_off"
    cmd = "turn_off" if text.decode('utf-8')[:2] == u"关闭" else "turn_on"

    if key in DEVICES:
        service = 'switch'
        requestService = url + service + "/" + cmd
        if key == u"儿歌":
             try:
                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(10)

                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(20)

                 data = json.dumps({'entity_id': DEVICES[u"上边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"上边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"右边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(4)

                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"下边"]})
                 response = post(requestService, data, headers=headers)
                 time.sleep(1)

                 data = json.dumps({'entity_id': DEVICES[u"确定"]})
                 response = post(requestService, data, headers=headers)
             except Exception as e:
                 mic.say(u"不能遥控打开" + text)
                 logger.error(e)
        else:
            if key == u"直播":
                try:
                    data = json.dumps({'entity_id': DEVICES[key]})
                    service = DEVICES[key].split('.')[0]
                    response = post(url + service + "/" + cmd, data, headers=headers)
                    logger.debug(response)
                    mic.say(text)
                except Exception as e:
                    mic.say(u"不能遥控打开" + text)
                    logger.error(e)
            else:
                mic.say(u"没听清你要看什么节目")
    else:
        mic.say(u"我没办法完成" + text + u"操作")


def isValid(text):
    for phrases in PHRASES:
        if text.startswith(phrases):
            return True
    return False
