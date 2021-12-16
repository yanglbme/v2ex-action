import os

from actions_toolkit import core

from app import log
from app.action import Action

os.environ[
    'INPUT_WEBHOOK'] = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=01a56312-d0cb-dffx-8f15-8821d8f3a9e2'
os.environ['INPUT_COUNT'] = '10'

try:
    hook = core.get_input('webhook', required=True)
    secret = core.get_input('secret')
    count = int(core.get_input('count') or 8)

    action = Action(hook, secret, count)
    action.run()
except Exception as e:
    log.set_failed(str(e))
