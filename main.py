from actions_toolkit import core

from app import log
from app.action import Action

author = {
    'name': 'Yang Libin',
    'link': 'https://github.com/yanglbme'
}
marketplace = 'https://github.com/marketplace/actions/v2ex-action'

log.info(f'Welcome to use V2EX Action ❤\n\n'
         f'📕 Getting Started Guide: {marketplace}\n'
         f'📣 Maintained by {author["name"]}: {author["link"]}\n')

try:
    hook = core.get_input('webhook', required=True)
    secret = core.get_input('secret')
    count = int(core.get_input('count') or 8)

    log.info('Start running V2EX Action')
    action = Action(hook, secret, count)
    action.run()

    log.info('Success, thanks for using @yanglbme/v2ex-action!')
except Exception as e:
    log.set_failed(str(e))
