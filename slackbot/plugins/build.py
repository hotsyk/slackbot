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
        build_in_progress = False
        return wait_till_end_of_build(message)
    else:
        message.send('>⛔ Stage build was halted')
        build_in_progress = False
        return


@listen_to('fuck')
@listen_to('no build')
@listen_to('ohrana otmena')
@listen_to('nonono')
@respond_to('stop')
def stop_stage_build(message):
    global stop_stage_build_flag
    global build_in_progress

    if build_in_progress:
        stop_stage_build_flag = True
        message.reply('Got it!')
    else:
        message.reply('Sorry, build already queued. \n'
                      'But you can cancel stage build with '
                      '"@buildbot: stop stage build".\n'
                      'Check help for more information')
    return


@respond_to('stop stage build')
def stop_running_build(message):
    message.reply('Looking for active stage builds:')
    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)
    my_job = J['stage']
    builds = [i for i in my_job.get_build_ids()]
    build = my_job.get_build(builds[0])
    if build.is_running():
        build.stop()
        message.reply('Build #{0} was stopped'.format(builds[0]))
    else:
        message.reply('Running build was not found')
    return


def wait_till_end_of_build(message):
    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)
    my_job = J['stage']
    builds = [i for i in my_job.get_build_ids()]
    build = my_job.get_build(builds[0])
    build_started = build.is_running()
    while build.is_running():
        sleep(10)

    if build_started:
        status = build.get_status()
        if status == 'SUCCESS':
            message.send('>✅ Build "{0}" finished.\n>'
                         'Check results here {1}'.format(
                             build.name, build.get_result_url()))
        else:
            message.send(
                '>❗ Build "{0}" failed\n>Check results here {1}'.format(
                    build.name, build.get_result_url()))
