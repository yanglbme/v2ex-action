import base64
import hashlib
import hmac
import json
import re
import time
import urllib.parse
from actions_toolkit.core import get_input

import requests
import requests.packages.urllib3
from actions_toolkit import core
from fake_useragent import UserAgent

requests.packages.urllib3.disable_warnings()


class Action:
    """V2EX Action"""

    timeout = 5
    ua = UserAgent()

    def __init__(self, hook, secret='', count=8):
        self.hook = hook
        self.secret = secret
        self.count = count
        self.contents = []
        self.res = False

    def wx(self):
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'content': f'### V2EX 当前热门\n{"".join(self.contents)}'
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            resp = requests.post(url=self.hook,
                                 headers=headers,
                                 data=json.dumps(data),
                                 timeout=Action.timeout,
                                 verify=False)
            self.res = resp.json()['errcode'] == 0
        except Exception as e:
            print(f'something error occurred, message: {e}')

    def ding(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc,
                             string_to_sign_enc,
                             digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = f'{self.hook}&timestamp={timestamp}&sign={sign}'
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'title': 'V2EX 当前热门',
                'text': f'### V2EX 当前热门\n{"".join(self.contents)}'
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            resp = requests.post(url=url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 timeout=Action.timeout,
                                 verify=False)
            self.res = resp.json()['errcode'] == 0
        except Exception as e:
            print(f'something error occurred, message: {e}')

    @staticmethod
    def get_v2ex_hot_topics():
        url = 'https://v2ex.com/?tab=hot'
        headers = {'User-Agent': Action.ua.random}
        contents = []
        try:
            resp = requests.get(url=url,
                                headers=headers,
                                timeout=Action.timeout,
                                verify=False)
            match = re.compile(
                '<span class="item_hot_topic_title">(.*?)</span>', re.DOTALL)
            for item in match.findall(resp.text):
                detail_url = 'https://v2ex.com' + re.search(
                    '<a href="(.*?)">', item.strip()).group(1)
                title = re.search('">(.*?)</a>', item.strip()).group(1)
                content = f'> - [{title}]({detail_url})\n'
                contents.append(content)
            return contents
        except Exception as e:
            print(f'something error occurred, message: {e}')
        return []

    def run(self):
        contents = Action.get_v2ex_hot_topics()
        self.contents = contents[:self.count]
        if 'weixin' in self.hook:
            self.wx()
        elif 'dingtalk' in self.hook:
            self.ding()
        print(f'::set-output name=result::{self.res}')


if __name__ == '__main__':
    input_hook = core.get_input('webhook')
    input_secret = core.get_input('secret', required=False)
    count_str = core.get_input('count')
    input_count = int(count_str) if count_str else 8
    action = Action(input_hook, input_secret, input_count)
    action.run()
