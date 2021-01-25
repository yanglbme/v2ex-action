from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    input_hook = core.get_input('webhook')
    input_secret = core.get_input('secret', required=False)
    count_str = core.get_input('count')
    input_count = int(count_str) if count_str else 8
    action = Action(input_hook, input_secret, input_count)
    try:
        action.run()
        core.info('V2EX Action Run Successfully.')
    except Exception as e:
        core.set_failed(str(e))
