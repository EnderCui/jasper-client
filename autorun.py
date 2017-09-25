# -*- coding:utf-8 -*-
import subprocess
import time
import sys

TIME = 12 * 60
CMD = "jasper.py"


class Auto_Run():
    def __init__(self, sleep_time, cmd):
        self.sleep_time = sleep_time
        self.cmd = cmd
        self.p = None
        self.run()
        try:
            while 1:
                time.sleep(sleep_time * 60)
                self.poll = self.p.poll()
                if self.poll is None:
                    print u"准备自动重启程序"
                    self.p.kill()
                    self.run()
                else:
                    print u"未检测到程序运行状态，准备启动程序"
                    self.run()
        except:
            self.p.kill()
            self.run()

    def run(self):
        print u"执行 python %s" % self.cmd
        self.p = subprocess.Popen(['python', '%s' % self.cmd],
                                  stdin=sys.stdin, stdout=sys.stdout,
                                  stderr=sys.stderr, shell=False)


app = Auto_Run(TIME, CMD)
