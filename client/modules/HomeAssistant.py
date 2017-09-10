# -*- coding: utf-8-*-
import re
import sys
import json
import logging
from requests import post

reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["HOMEASSISTANT"]
SLUG = "home_assistant"

PHRASES = [u"打开", u"关闭"]

DEVICES = {u"电视": 'media_player.sony_bravia_tv', u"格力空调": 'switch.gree_ac_power', \
           u"美的空调": 'switch.midea_ac_power', u"盒子": 'switch.damai_box_power', \
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
    text = text.strip().replace("，","").replace("。","")
    key = text.decode('utf-8')[2:]
    cmd = "turn_on" if text.decode('utf-8')[:2] == u"打开" else "turn_off"

    if DEVICES.has_key(key):
        data = json.dumps({'entity_id':DEVICES[key]})
        service = DEVICES[key].split('.')[0]
        try:
            response = post(url + service + "/" + cmd, data, headers=headers)
            mic.say(u"已经" + text)
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
