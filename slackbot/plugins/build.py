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
    message.reply('Roger that')
    for i in xrange(5):
        if stop_stage_build_flag:
            break
        else:
            if i in [0, 4]:
                message.send('>🕐 Stage build in {0} sec'.format(50 - i * 10))
            sleep(10)
    if not stop_stage_build_flag:
        build_in_progress = False

        J = Jenkins(settings.JENKINS_URL,
                    username=settings.JENKINS_USERNAME,
                    password=settings.JENKINS_PASSWORD)
        my_job = J['stage']
        my_job.invoke()

        while my_job.is_queued():
            sleep(5)

        builds = [i for i in my_job.get_build_ids()]
        build = my_job.get_build(builds[0])
        message.send('> 🔥 Started build #{0}'.format(builds[0]))

        while build.is_running():
            sleep(10)

        build = my_job.get_build(builds[0])
        status = build.get_status()
        if status == 'SUCCESS':
            message.send('>✅ Build "{0}" finished.\n>'
                         'Check results here {1}'.format(
                             build.name, build.get_result_url()))
        elif status == 'ABORTED':
            message.send(
                '>❌ Build "{0}" aborted\n>Check results here {1}'.format(
                    build.name, build.get_result_url()))
        else:
            message.send(
                '>❗ Build "{0}" failed\n>Check results here {1}'.format(
                    build.name, build.get_result_url()))

    else:
        message.send('>⛔ Stage build was halted')
        build_in_progress = False
        return


@listen_to('fuck')
@listen_to('no build')
@listen_to('ohrana otmena')
@listen_to('nonono')
@respond_to('stop')
@respond_to('terminate')
def stop_stage_build(message):
    global stop_stage_build_flag
    global build_in_progress

    if build_in_progress:
        stop_stage_build_flag = True
        message.reply('Roger that')
    else:
        message.reply('Looking for active stage builds....')
        J = Jenkins(settings.JENKINS_URL,
                    username=settings.JENKINS_USERNAME,
                    password=settings.JENKINS_PASSWORD)
        my_job = J['stage']

        while my_job.is_queued():
            sleep(5)

        builds = [i for i in my_job.get_build_ids()]
        build = my_job.get_build(builds[0])
        if build.is_running():
            build.stop()
            message.reply('Build #{0} was terminated.'.format(builds[0]))
        else:
            message.reply('Active build was not found.')


@listen_to('stage status')
def stage_status(message):
    global stop_stage_build_flag
    global build_in_progress

    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)
    my_job = J['stage']

    if build_in_progress or my_job.is_queued():
        message.send('>🕐 Build is enqueued')
    else:
        builds = [i for i in my_job.get_build_ids()]
        build = my_job.get_build(builds[0])
        status = build.get_status()
        if status == 'SUCCESS':
            message.send(
                '>✅ Last build "{0}" was a huge success: {1}'.format(
                    build.name, build.get_result_url()))
        elif status == 'ABORTED':
            message.send(
                '>❌ Last build "{0}" was aborted: {1}'.format(
                    build.name, build.get_result_url()))
        else:
            message.send(
                '>❗ Last build "{0}" failed: {1}'.format(
                    build.name, build.get_result_url()))
