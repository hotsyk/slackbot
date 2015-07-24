# coding: utf-8
from time import sleep

from jenkinsapi.jenkins import Jenkins

from slackbot import settings
from slackbot.bot import respond_to, listen_to


stop_stage_build_flag = False
build_in_progress = False


@respond_to('stage build')
def stage_build(message):
    global stop_stage_build_flag
    global build_in_progress

    build_in_progress = True
    stop_stage_build_flag = False

    for i in xrange(5):
        if stop_stage_build_flag:
            break
        else:
            if i in [0, 4]:
                message.send('>🕐 Stage build in {0} sec'.format(50 - i * 10))
            sleep(10)
    if not stop_stage_build_flag:
        J = Jenkins(settings.JENKINS_URL,
                    username=settings.JENKINS_USERNAME,
                    password=settings.JENKINS_PASSWORD)
        my_job = J['stage']
        res = my_job.invoke()
        message.send('> 🔥 Started build {0}'.format(res))
    else:
        message.send('>⛔ Stage build was halted')
    build_in_progress = False


@listen_to('fuck')
@listen_to('no build')
@listen_to('ohrana otmena')
@listen_to('nonono')
@respond_to('stop')
def stop_stage_build(message):
    global stop_stage_build_flag
    stop_stage_build_flag = True


@respond_to('sudo make me a sandwich')
def sandwich(message):
    message.reply('Sure! I am on my way!')
