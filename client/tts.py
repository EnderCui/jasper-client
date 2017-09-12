# -*- coding: utf-8-*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    is_available - returns True if the platform supports this implementation
"""
import os
import base64
import platform
import re
import tempfile
import subprocess
import pipes
import logging
import urllib
import httplib
import requests
import datetime
import hashlib
import hmac
from abc import ABCMeta, abstractmethod
from uuid import getnode as get_mac
import argparse
import yaml

import diagnose
import jasperpath

import sys
reload(sys)
sys.setdefaultencoding('utf8')


class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        config = cls.get_config()
        instance = cls(**config)
        return instance

    @classmethod
    @abstractmethod
    def is_available(cls):
        return diagnose.check_executable('aplay')

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def say(self, phrase, *args):
        pass

    def play(self, filename):
        cmd = ['aplay', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)


class AbstractMp3TTSEngine(AbstractTTSEngine):
    """
    Generic class that implements the 'play' method for mp3 files
    """
    @classmethod
    def is_available(cls):
        return (super(AbstractMp3TTSEngine, cls).is_available() and
                diagnose.check_python_import('mad'))

    def play_mp3(self, filename, remove=False):
        cmd = ['play', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)


class SimpleMp3Player(AbstractMp3TTSEngine):
    """
    MP3 player for playing mp3 files
    """
    SLUG = "mp3-player"

    @classmethod
    def is_available(cls):
        return True

    def say(self, phrase):
        self._logger.info(phrase)


class DummyTTS(AbstractTTSEngine):
    """
    Dummy TTS engine that logs phrases with INFO level instead of synthesizing
    speech.
    """

    SLUG = "dummy-tts"

    @classmethod
    def is_available(cls):
        return True

    def say(self, phrase):
        self._logger.info(phrase)

    def play(self, filename):
        self._logger.debug("Playback of file '%s' requested")
        pass


class EkhoTTS(AbstractTTSEngine):
    SLUG = "ekho-tts"

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and
                diagnose.check_executable('ekho'))

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['ekho', '-o', fname, phrase]
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)

class VoicerssTTS(AbstractMp3TTSEngine):
    SLUG = "voicerss-tts"

    def __init__(self, api_key):
        self._logger = logging.getLogger(__name__)
        self.api_key = api_key

    @classmethod
    def get_config(cls):
        config = {}
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'voicerss' in profile:
                    if 'api_key' in profile['voicerss']:
                        config['api_key'] = \
                            profile['voicerss']['api_key']
        return config

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

    def speech(self, settings):
        self.validate(settings)
        return self.request(settings)

    def validate(self, settings):
        if not settings:
            raise RuntimeError('The settings are undefined')
        if 'key' not in settings or not settings['key']:
            raise RuntimeError('The API key is undefined')
        if 'src' not in settings or not settings['src']:
            raise RuntimeError('The text is undefined')
        if 'hl' not in settings or not settings['hl']:
            raise RuntimeError('The language is undefined')

    def request(self, settings):
        result = {'error': None, 'response': None}

        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        params = urllib.urlencode(self.buildRequest(settings))

        if 'ssl' in settings and settings['ssl']:
            conn = httplib.HTTPSConnection('api.voicerss.org:443')
        else:
            conn = httplib.HTTPConnection('api.voicerss.org:80')

        conn.request('POST', '/', params, headers)

        response = conn.getresponse()
        content = response.read()

        if response.status != 200:
            result['error'] = response.reason
        elif content.find('ERROR') == 0:
            result['error'] = content
        else:
            result['response'] = content

        conn.close()

        return result

    def buildRequest(self, settings):
        params = {'key': '', 'src': '', 'hl': '', 'r': '', 'c': '', 'f': '', 'ssml': '', 'b64': ''}

        if 'key' in settings: params['key'] = settings['key']
        if 'src' in settings: params['src'] = settings['src']
        if 'hl' in settings: params['hl'] = settings['hl']
        if 'r' in settings: params['r'] = settings['r']
        if 'c' in settings: params['c'] = settings['c']
        if 'f' in settings: params['f'] = settings['f']
        if 'ssml' in settings: params['ssml'] = settings['ssml']
        if 'b64' in settings: params['b64'] = settings['b64']

        return params

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        voice = self.speech({
            'key': self.api_key,
            'hl': 'zh-cn',
            'src': phrase,
            'r': '0',
            'c': 'mp3',
            'f': '44khz_16bit_stereo',
            'ssml': 'false',
            'b64': 'false'
        })
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(voice['response'])
            tmpfile = f.name
        if tmpfile is not None:
            self.play_mp3(tmpfile)
            os.remove(tmpfile)

class BaiduTTS(AbstractMp3TTSEngine):
    SLUG = "baidu-tts"

    def __init__(self, api_key, secret_key, per=0):
        self._logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.secret_key = secret_key
        self.per = per
        self.token = ''

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # Try to get baidu_yuyin config from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'baidu_yuyin' in profile:
                    if 'api_key' in profile['baidu_yuyin']:
                        config['api_key'] = \
                            profile['baidu_yuyin']['api_key']
                    if 'secret_key' in profile['baidu_yuyin']:
                        config['secret_key'] = \
                            profile['baidu_yuyin']['secret_key']
                    if 'per' in profile['baidu_yuyin']:
                        config['per'] = \
                            profile['baidu_yuyin']['per']
        return config

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

    def get_token(self):
        URL = 'http://openapi.baidu.com/oauth/2.0/token'
        params = urllib.urlencode({'grant_type': 'client_credentials',
                                   'client_id': self.api_key,
                                   'client_secret': self.secret_key})
        r = requests.get(URL, params=params)
        try:
            r.raise_for_status()
            token = r.json()['access_token']
            return token
        except requests.exceptions.HTTPError:
            self._logger.critical('Token request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return ''

    def split_sentences(self, text):
        punctuations = ['.', '。', ';', '；', '\n']
        for i in punctuations:
            text = text.replace(i, '@@@')
        return text.split('@@@')

    def get_speech(self, phrase):
        if self.token == '':
            self.token = self.get_token()
        query = {'tex': phrase,
                 'lan': 'zh',
                 'tok': self.token,
                 'ctp': 1,
                 'cuid': str(get_mac())[:32],
                 'per': self.per
                 }
        r = requests.post('http://tsn.baidu.com/text2audio',
                          data=query,
                          headers={'content-type': 'application/json'})
        try:
            r.raise_for_status()
            if r.json()['err_msg'] is not None:
                self._logger.critical('Baidu TTS failed with response: %r',
                                      r.json()['err_msg'],
                                      exc_info=True)
                return None
        except Exception:
            pass
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(r.content)
            tmpfile = f.name
            return tmpfile

    def say(self, phrase):
        self._logger.debug(u"Saying '%s' with '%s'", phrase, self.SLUG)
        tmpfile = self.get_speech(phrase)
        if tmpfile is not None:
            self.play(tmpfile)
            os.remove(tmpfile)

class AliyunTTS(AbstractTTSEngine):
    SLUG = "aliyun-tts"

    def __init__(self, ak_id, ak_secret):
        self._logger = logging.getLogger(__name__)
        self.ak_id = ak_id
        self.ak_secret = ak_secret

    @classmethod
    def get_config(cls):
        config = {}
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'aliyun' in profile:
                    if 'ak_id' in profile['aliyun']:
                        config['ak_id'] = \
                            profile['aliyun']['ak_id']
                    if 'ak_secret' in profile['aliyun']:
                        config['ak_secret'] = \
                            profile['aliyun']['ak_secret']
        return config

    def get_authorization(self, phrase, date):
        bodyMd5 = base64.b64encode(hashlib.md5(phrase).digest())
        #md52 = base64.b64encode(hashlib.md5(bodyMd5).digest())

        method = "POST"
        accept = "audio/wav, application/json"
        content_type = "text/plain"
        stringToSign = method + "\n" + accept + "\n" + bodyMd5 + "\n" + content_type + "\n" + date
        signature = base64.b64encode(hmac.new(self.ak_secret, stringToSign, hashlib.sha1).digest())

        authHeader = "Dataplus " + self.ak_id + ":" + signature
        return authHeader

    def get_gmttime(self):
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)

    def get_speech(self, phrase):
        url = "http://nlsapi.aliyun.com/speak?encode_type=wav&voice_name=xiaoyun&volume=50"
        date = self.get_gmttime()
        r = requests.post(url,
                          data=phrase,
                          headers={'Authorization': self.get_authorization(phrase, date),
                          'Content-type': 'text/plain',
                          'Accept': 'audio/wav, application/json',
                          'Date': date,
                          'Content-Length': str(len(phrase))})

        try:
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(r.content)
                tmpfile = f.name
                return tmpfile
        except Exception:
            if 'error_code' in r.json():
                self._logger.critical('Aliyun TTS failed with response: %r',
                                      r.json()['error_code'],
                                      exc_info=True)
                return None

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

    def say(self, phrase):
        self._logger.debug(u"Saying '%s' with '%s'", phrase, self.SLUG)
        tmpfile = self.get_speech(phrase.encode('utf-8'))
        if tmpfile is not None:
            self.play(tmpfile)
            os.remove(tmpfile)

def get_default_engine_slug():
    return 'osx-tts' if platform.system().lower() == 'darwin' else 'ekho-tts'


def get_engine_by_slug(slug=None):
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No TTS engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple TTS engines found for slug '%s'. " +
                  "This is most certainly a bug." % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("TTS engine '%s' is not available (due to " +
                              "missing dependencies, etc.)") % slug)
        return engine


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in
            list(get_subclasses(AbstractTTSEngine))
            if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper TTS module')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug messages')
    args = parser.parse_args()

    logging.basicConfig()
    if args.debug:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

    engines = get_engines()
    available_engines = []
    for engine in get_engines():
        if engine.is_available():
            available_engines.append(engine)
    disabled_engines = list(set(engines).difference(set(available_engines)))
    print("Available TTS engines:")
    for i, engine in enumerate(available_engines, start=1):
        print("%d. %s" % (i, engine.SLUG))

    print("")
    print("Disabled TTS engines:")

    for i, engine in enumerate(disabled_engines, start=1):
        print("%d. %s" % (i, engine.SLUG))

    print("")
    for i, engine in enumerate(available_engines, start=1):
        print("%d. Testing engine '%s'..." % (i, engine.SLUG))
        engine.get_instance().say("This is a test.")
    print("Done.")
