# -*- coding: utf-8-*-
import subprocess
import logging
import os

WORDS = ["TUICHU"]
SLUG = "quit"


def handle(text, mic, profile, bot=None):
    logger = logging.getLogger(__name__)
    grep_cmd = "ps aux | grep 'python jasper.py' | grep -v grep"
    try:
        p = subprocess.Popen(
            grep_cmd,
            stdout=subprocess.PIPE, shell=True)
        p.wait()
        lines = p.stdout.readlines()

        for line in lines:
            if str(os.getpid()) == line.split()[1]:
                continue
            kill_cmd = "kill -9 " + line.split()[1]

            p = subprocess.Popen(
                kill_cmd,
                stdout=subprocess.PIPE, shell=True)
            p.wait()

        mic.say(u"再见")

        kill_cmd = "kill -9 " + str(os.getpid())

        p = subprocess.Popen(
            kill_cmd,
            stdout=subprocess.PIPE, shell=True)
        p.wait()

    except Exception, e:
        logger.error(e)
        mic.say(u'抱歉，运行失败')


def isValid(text):
    return any(word in text for word in [u"退出", u"停止"])
