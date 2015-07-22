from slackbot.bot import respond_to, listen_to
import re


@listen_to('help build')
@respond_to('hello$', re.IGNORECASE)
@respond_to('help$', re.IGNORECASE)
def hello_reply(message):
    message.reply('Hello! I am @buildbot and I can start stage build\n'
                  'You can start new stage build by typing:\n'
                  '>@buildbot: stage build\n'
                  'To stop build during countdown, type either:\n'
                  '>@buildbot: stop\n'
                  '>ohrana otmena\n'
                  '>no build\n'
                  'I am pleased to help you.')
