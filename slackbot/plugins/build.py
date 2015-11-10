# coding: utf-8
import datetime
import pytz
import random

from time import sleep

from jenkinsapi.jenkins import Jenkins

from slackbot import settings
from slackbot.bot import respond_to, listen_to


stop_stage_build_flag = False
build_in_progress = False

quotes = [
    'Hahahahaha. Oh wait you’re serious. Let me laugh even harder.',
    'Anything less than immortality is a complete waste of time.',
    'Shut up baby, I know it!',
    'I\'m back baby',
    'Let\'s go alredaaaayyy!',
    'Some day we\'ll be able to look back on this whole thing and laugh...'
    'AH HA HA HA!!!!',
    'I\'m not getting you down at all, am I?',
    'Funny, how just when you think life can\'t possibly get any worse '
    'it suddenly does.',
    'Wearily I sit here, pain and misery my only companions.',
    'I won\'t enjoy it.',
    'Life! Don\'t talk to me about life.',
    'It’s not my fault.',
    'Do. Or do not. There is no try.',
    'Somebody has to save our skins.',
    'In my experience there is no such thing as luck.',
    'I\'ve got a bad feeling about this.',
    'Your eyes can deceive you. Don’t trust them.',
    'Never tell me the odds.',
    'Stay on target.',
    'This is a new day, a new beginning.',
    'May the Force be with you',
    'Use the force, Luke.',
    'Mmm. Lost a planet, Master Obi-Wan has. How embarrassing.',
    'If there\'s a bright centre to the universe, you\'re on '
    'the planet that it\'s farthest from.',
    'Fear is the path to the dark side.',
    'I find your lack of faith disturbing.',
    'There\'s always a bigger fish.',
    'Hello. I don\'t believe we have been introduced. R2-D2? '
    'A pleasure to meet you. I am C-3PO, Human-Cyborg Relations.',
    'Ahh, hard to see, the Dark Side is.',
    'Sir, the possibility of successfully navigating an asteroid '
    'field is approximately 3,720 to 1.',
    'Obi-Wan has taught you well.',
    'I suggest a new strategy, R2: let the Wookiee win.',
    'Remember...the Force will be with you, always.',
    'Don\'t Panic!',
    'Would it save you a lot of time if I just gave up and went mad now?',
    'You\'re turning into a penguin. Stop it.',
    'So long, and thanks for all the fish.',

]


@listen_to('stage build')
@respond_to('stage build')
def stage_build(message):
    global stop_stage_build_flag
    global build_in_progress

    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)
    my_job = J['stage']

    build = my_job.get_last_build()
    if build.is_running() or my_job.is_queued() or build_in_progress:
        return stage_status(message)

    build_in_progress = True
    stop_stage_build_flag = False
    message.reply(random.choice(quotes))

    for i in xrange(5):
        if stop_stage_build_flag:
            break
        else:
            if i in [0, 4]:
                message.send('>🕐 Stage build in {0} sec'.format(50 - i * 10))
            sleep(10)
    if not stop_stage_build_flag:
        build_in_progress = False

        my_job.invoke()

        while my_job.is_queued():
            sleep(5)

        build = my_job.get_last_build()
        message.send('> 🔥 Started build #{0}'.format(build))

        while build.is_running():
            sleep(10)

        build = my_job.get_last_build()
        status = build.get_status()
        if status == 'SUCCESS':
            message.send('>✅ Build "{0}" finished.\n>'
                         'Check results here {1}'.format(
                             build.name, build.baseurl))
            ikarus_status(message, build.buildno)
        elif status == 'ABORTED':
            message.send(
                '>❌ Build "{0}" aborted\n>Check results here {1}'.format(
                    build.name, build.baseurl))
        else:
            message.send(
                '>❗ Build "{0}" failed\n>Check results here {1}'.format(
                    build.name, build.baseurl))

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
        message.reply(random.choice(quotes))
    else:
        message.reply('Looking for active stage builds....')
        J = Jenkins(settings.JENKINS_URL,
                    username=settings.JENKINS_USERNAME,
                    password=settings.JENKINS_PASSWORD)
        my_job = J['stage']

        while my_job.is_queued():
            sleep(5)

        build = my_job.get_last_build()
        if build.is_running():
            build.stop()
            message.reply('Stage build #{0} was terminated.'.format(build))
        else:
            message.reply('Active build was not found.')


def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%d day(s) %d hour(s) %d min(s) %d sec(s)' % (days, hours,
                                                             minutes, seconds)
    elif hours > 0:
        return '%d hour(s) %d min(s) %d sec(s)' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%d min(s) %d sec(s)' % (minutes, seconds)
    else:
        return '%d sec(s)' % (seconds,)


@listen_to('stage status')
@respond_to('stage status')
def stage_status(message):
    global stop_stage_build_flag
    global build_in_progress

    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)
    my_job = J['stage']

    if build_in_progress or my_job.is_queued():
        message.send('>🕐 Stage build is enqueued')
    else:
        build = my_job.get_last_build()
        status = build.get_status()
        time_since_build = pretty_time_delta(
            (datetime.datetime.now(pytz.utc) -
             build.get_timestamp()).total_seconds()
        )
        if build.is_running():
            message.send('>🕐 Build "{0}" is in progress. '
                         'It was started {1} ago: {2}'.format(
                             build.name, time_since_build,
                             build.baseurl))
        elif status == 'SUCCESS':
            message.send(
                '>✅ Last build "{0}" was started {1} ago and '
                'had succeeded: {2}'.format(
                    build.name, time_since_build,
                    build.baseurl))
        elif status == 'ABORTED':
            message.send(
                '>❌ Last build "{0}" was started {1} ago and was aborted: '
                '{2}'.format(
                    build.name, time_since_build,
                    build.baseurl))
        else:
            message.send(
                '>❗ Last build "{0}" started {1} ago and had failed: '
                '{2}'.format(
                    build.name, time_since_build,
                    build.baseurl))


def _get_ikarus_build(stage_build_no, ikarus_job):
    for ib in ikarus_job.get_build_ids():
        build = ikarus_job.get_build(ib)
        for action in build.get_actions()['causes']:
            if action.get('upstreamBuild') == stage_build_no:
                return build
    return None


@listen_to('ikarus status')
@respond_to('ikarus status')
def ikarus_status(message, stage_build_no=None):
    J = Jenkins(settings.JENKINS_URL,
                username=settings.JENKINS_USERNAME,
                password=settings.JENKINS_PASSWORD)

    if stage_build_no:
        ikarus_job = 'ikarus-stage-regression-bvt'
    else:
        ikarus_job = 'ikarus-stage-monitor'

    ikarus_notify_users = '@dzvezdov, @yrazdolskiy, @kaydanowski'

    my_job = J[ikarus_job]

    if not stage_build_no:
        if my_job.is_queued():
            message.send('>🕐 Ikarus build is enqueued')

    while my_job.is_queued():
        sleep(10)

    if stage_build_no:
        build = _get_ikarus_build(stage_build_no, my_job)
        if not build:
            message.send('>❌ Not found Ikarus monitor build for upstream '
                         'stage build {0}'.format(stage_build_no))
            return
    else:
        build = my_job.get_last_build()

    if stage_build_no:
        while build.is_running():
            sleep(10)

    build = my_job.get_build(build.buildno)

    status = build.get_status()
    time_since_build = pretty_time_delta(
        (datetime.datetime.now(pytz.utc) -
         build.get_timestamp()).total_seconds()
    )
    if build.is_running():
        message.send('>🕐 Build "{0}" is in progress. '
                     'It was started {1} ago: {2}'.format(
                         build.name, time_since_build,
                         build.baseurl))
    elif status == 'SUCCESS':
        message.send(
            '>✅ Last build "{0}" was started {1} ago and '
            'had succeeded: {2}'.format(
                build.name, time_since_build,
                build.baseurl))
    elif status == 'ABORTED':
        message.send(
            '>❌ Last build "{0}" was started {1} ago and was aborted: '
            '{2}\n ATTN: {3}'.format(
                build.name, time_since_build,
                build.baseurl,
                ikarus_notify_users
            ))
    else:
        message.send(
            '>❗ Last build "{0}" started {1} ago and had failed: '
            '{2}\n ATTN: {3}'.format(
                build.name, time_since_build,
                build.baseurl,
                ikarus_notify_users
            ))
