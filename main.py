from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    try:
        input_hook = core.get_input('webhook', required=True)
        input_secret = core.get_input('secret')
        count_str = core.get_input('count')
        input_count = int(count_str) if count_str else 8

        action = Action(input_hook, input_secret, input_count)
        action.run()
    except Exception as e:
        core.set_failed(str(e))
