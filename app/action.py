import base64
import hashlib
import hmac
import json
import re
import time
import urllib.parse

import requests
import requests.packages.urllib3

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'

requests.packages.urllib3.disable_warnings()


class Action:
    """V2EX Action"""

    timeout = 5

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
        resp = requests.post(url=self.hook,
                             headers=headers,
                             data=json.dumps(data),
                             timeout=Action.timeout,
                             verify=False)
        self.res = resp.json()['errcode'] == 0

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
        requests.post(url=url,
                      headers=headers,
                      data=json.dumps(data),
                      timeout=Action.timeout,
                      verify=False)

    @staticmethod
    def get_v2ex_hot_topics():
        url = 'https://v2ex.com/?tab=hot'
        headers = {'User-Agent': USER_AGENT}
        contents = []
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

    def run(self):
        contents = Action.get_v2ex_hot_topics()
        self.contents = contents[:self.count]
        if 'weixin' in self.hook:
            self.wx()
        elif 'dingtalk' in self.hook:
            self.ding()
