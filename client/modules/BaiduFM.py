# -*- coding: utf-8-*-
import json
import logging
import socket
import sys
from urllib import urlopen
from omxplayer.player import OMXPlayer

reload(sys)
sys.setdefaultencoding('utf8')
socket.setdefaulttimeout(10)

WORDS = ["BAIDUYINYUE"]
SLUG = "baidufm"

DEFAULT_CHANNEL = 14


class MusicPlayer():

    def __init__(self, playlist, logger):
        self.playlist = playlist
        self.idx = 0
        self.logger = logger
        self.omxplayer = None

    def get_song_real_url(self, song_url):
        try:
            htmldoc = urlopen(song_url).read().decode('utf8')
        except:
            return(None, None, 0, 0)

        content = json.loads(htmldoc)

        try:
            song_link = content['data']['songList'][0]['songLink']
            song_name = content['data']['songList'][0]['songName']
            song_size = int(content['data']['songList'][0]['size'])
            song_time = int(content['data']['songList'][0]['time'])
        except:
            self.logger.error('get real link failed')
            return(None, None, 0, 0)

        return song_name, song_link, song_size, song_time

    def play(self):
        self.logger.debug('MusicPlayer play')
        song_url = "http://music.baidu.com/data/music/fmlink?" +\
            "type=mp3&rate=320&songIds=%s" % self.playlist[self.idx]['id']
        song_name, song_link, song_size, song_time =\
            self.get_song_real_url(song_url)

        self.play_mp3_by_link(song_link, song_name, song_size, song_time)

    def play_mp3_by_link(self, song_link, song_name, song_size, song_time):
        if song_link:
            self.omxplayer = OMXPlayer(song_link, ['-o', 'both'])
        else:
            self.omxplayer = None

    def pick_next(self):
        self.idx += 1
        if self.idx > len(self.playlist) - 1:
            self.idx = 0

        if self.omxplayer and self.omxplayer.can_play():
            self.omxplayer.quit()

    def pick_previous(self):
        self.idx -= 1
        if self.idx < 0:
            self.idx = 0

        if self.omxplayer and self.omxplayer.can_play():
            self.omxplayer.quit()

    def pause(self):
        if self.omxplayer and self.omxplayer.can_pause():
            self.omxplayer.pause()

    def resume(self):
        if self.omxplayer and self.omxplayer.can_play():
            self.omxplayer.play()

    def is_play_done(self):
        try:
            return self.omxplayer is None or\
                self.omxplayer.can_play() is None
        except Exception as e:
            self.logger.error(e)
            return False

    def stop(self):
        self.playlist = []
        if self.omxplayer:
            self.omxplayer.quit()


def get_channel_list(page_url):
    try:
        htmldoc = urlopen(page_url).read().decode('utf8')
    except:
        return {}

    content = json.loads(htmldoc)
    channel_list = content['channel_list']

    return channel_list


def get_song_list(channel_url):
    try:
        htmldoc = urlopen(channel_url).read().decode('utf8')
    except:
        return{}

    content = json.loads(htmldoc)
    song_id_list = content['list']

    return song_id_list


def handle(text, mic, profile, bot=None):
    logger = logging.getLogger(__name__)
    page_url = 'http://fm.baidu.com/dev/api/?tn=channellist'
    channel_list = get_channel_list(page_url)

    if 'robot_name' in profile:
        persona = profile['robot_name']

    channel = DEFAULT_CHANNEL

    if SLUG in profile and 'channel' in profile[SLUG]:
        channel = profile[SLUG]['channel']

    channel_id = channel_list[channel]['channel_id']
    channel_name = channel_list[channel]['channel_name']
    mic.say(u"播放" + channel_name)

    while True:
        channel_url = 'http://fm.baidu.com/dev/api/' +\
            '?tn=playlist&format=json&id=%s' % channel_id
        song_id_list = get_song_list(channel_url)
        music_player = MusicPlayer(song_id_list, logger)

        while True:
            music_player.play()

            while True:
                if music_player.is_play_done():
                    music_player.pick_next()
                    break
                try:
                    threshold, transcribed = mic.passiveListen(persona)
                except Exception, e:
                    logger.error(e)
                    threshold, transcribed = (None, None)

                if not transcribed or not threshold:
                    logger.info("Nothing has been said or transcribed.")
                    continue

                music_player.pause()
                input = mic.activeListen()

                if input:
                    if any(ext in input for ext in [u"结束", u"退出", u"停止"]):
                        mic.say(u"结束播放")
                        music_player.stop()
                        return
                    elif any(ext in input for ext in [u"下一首", u"切换"]):
                        music_player.pick_next()
                        music_player.play()
                    elif any(ext in input for ext in [u"上一首"]):
                        music_player.pick_previous()
                        music_player.play()
                    elif any(ext in input for ext in [u"暂停"]):
                        continue
                    elif any(ext in input for ext in [u"播放", u"恢复"]):
                        music_player.resume()
                    else:
                        music_player.resume()
                else:
                    mic.say(u"什么？")
                    music_player.resume()


def isValid(text):
    return any(word in text for word in [u"百度音乐", u"百度电台"])
