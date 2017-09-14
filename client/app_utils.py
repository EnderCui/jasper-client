# -*- coding: utf-8-*-
import smtplib
from email.MIMEText import MIMEText
import urllib2
import re
import logging
from pytz import timezone
import time
import subprocess

def sendEmail(SUBJECT, BODY, TO, FROM, SENDER, PASSWORD, SMTP_SERVER):
    """Sends an HTML email."""
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            BODY.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
    msg = MIMEText(BODY.encode(body_charset), 'html', body_charset)
    msg['From'] = SENDER
    msg['To'] = TO
    msg['Subject'] = SUBJECT

    SMTP_PORT = 587
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.starttls()
    session.login(FROM, PASSWORD)
    session.sendmail(SENDER, TO, msg.as_string())
    session.quit()


def emailUser(profile, SUBJECT="", BODY=""):
    """
    sends an email.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
        SUBJECT -- subject line of the email
        BODY -- body text of the email
    """
    def generateSMSEmail(profile):
        """
        Generates an email from a user's phone number based on their carrier.
        """
        if profile['carrier'] is None or not profile['phone_number']:
            return None

        return str(profile['phone_number']) + "@" + profile['carrier']

    if profile['prefers_email'] and profile['gmail_address']:
        # add footer
        if BODY:
            BODY = profile['first_name'] + \
                ",<br><br>Here are your top headlines:" + BODY
            BODY += "<br>Sent from your Jasper"

        recipient = profile['gmail_address']
        if profile['first_name'] and profile['last_name']:
            recipient = profile['first_name'] + " " + \
                profile['last_name'] + " <%s>" % recipient
    else:
        recipient = generateSMSEmail(profile)

    if not recipient:
        return False

    try:
        if 'mailgun' in profile:
            user = profile['mailgun']['username']
            password = profile['mailgun']['password']
            server = 'smtp.mailgun.org'
        else:
            user = profile['gmail_address']
            password = profile['gmail_password']
            server = 'smtp.gmail.com'
        sendEmail(SUBJECT, BODY, recipient, user,
                  "Jasper <jasper>", password, server)

        return True
    except:
        return False


def getTimezone(profile):
    """
    Returns the pytz timezone for a given profile.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
    """
    try:
        return timezone(profile['timezone'])
    except:
        return None


def generateTinyURL(URL):
    """
    Generates a compressed URL.

    Arguments:
        URL -- the original URL to-be compressed
    """
    target = "http://tinyurl.com/api-create.php?url=" + URL
    response = urllib2.urlopen(target)
    return response.read()


def isNegative(phrase):
    """
    Returns True if the input phrase has a negative sentiment.

    Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(no(t)?|don\'t|stop|end)\b', phrase,
                          re.IGNORECASE))


def isPositive(phrase):
    """
        Returns True if the input phrase has a positive sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(sure|yes|yeah|go)\b', phrase, re.IGNORECASE))


def create_reminder(remind_event, remind_time):
    if len(remind_time) == 14:
        cmd = 'task add ' + remind_event + ' due:' +\
            remind_time[:4] + '-' + remind_time[4:6] + '-' + \
            remind_time[6:8] + 'T' + remind_time[8:10] + ':' + \
            remind_time[10:12] + ':' + remind_time[12:]
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, shell=True)
            p.wait()
            line = p.stdout.readline()

            if 'Created task' in line:
                return True
        except:
            return False
    else:
        return False


def get_due_reminders():
    task_ids = []
    due_tasks = []
    _logger = logging.getLogger(__name__)
    try:
        p = subprocess.Popen(
            'task status:pending count',
            stdout=subprocess.PIPE, shell=True)
        p.wait()

        pending_task_num = int(p.stdout.readline())

        p = subprocess.Popen(
            'task list',
            stdout=subprocess.PIPE, shell=True)
        p.wait()
        lines = p.stdout.readlines()[3:(3 + pending_task_num)]
        for line in lines:
            task_ids.append(line.split()[0])

        now = int(time.strftime('%Y%m%d%H%M%S'))

        for id in task_ids:

            p = subprocess.Popen(
                'task _get ' + id + '.due',
                stdout=subprocess.PIPE, shell=True)
            p.wait()
            due_time = p.stdout.readline()
            due_time_format = int(
                due_time[:4] + due_time[5:7] + due_time[8:10] +
                due_time[11:13] + due_time[14:16] + due_time[17:19])
            if due_time_format <= now:
                p = subprocess.Popen(
                    'task _get ' + id + '.description',
                    stdout=subprocess.PIPE, shell=True)
                p.wait()
                event = p.stdout.readline()
                due_tasks.append(event.strip('\n') + u',时间到了')
                cmd = 'task delete ' + id
                p = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE)
                p.stdin.write('yes\n')

    except Exception, e:
        _logger.error(e)

    return due_tasks
