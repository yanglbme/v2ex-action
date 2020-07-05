import base64
import hashlib
import hmac
import json
import os
import random
import re
import time
import urllib.parse

import requests

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; "
    "SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; "
    "SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; "
    "Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; "
    "Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; "
    "Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; "
    "Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) "
    "AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) "
    "Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ "
    "(KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; "
    "rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) "
    "Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) "
    "Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) "
    "Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 "
    "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
    "AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) "
    "Presto/2.9.168 Version/11.52"
]
TIMEOUT = 5


class Action:
    """V2EX Action"""

    def __init__(self):
        self.hook = os.environ['INPUT_WEBHOOK']
        self.secret = os.environ['INPUT_SECRET'] or ''
        self.count = int(os.environ['INPUT_COUNT']) or 8
        self.contents = []
        self.res = False

    def wx(self):
        """调用企业微信机器人接口"""
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'content': f'### V2EX 当前热门\n{"".join(self.contents)}'
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            resp = requests.post(self.hook,
                                 headers=headers,
                                 data=json.dumps(data),
                                 timeout=TIMEOUT)
            self.res = resp.json()['errcode'] == 0
        except Exception as e:
            print(f'something error occurred, message: {e}')

    def ding(self):
        """调用钉钉机器人"""
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
            resp = requests.post(url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 timeout=TIMEOUT)
            self.res = resp.json()['errcode'] == 0
        except Exception as e:
            print(f'something error occurred, message: {e}')

    @staticmethod
    def get_v2ex_hot_topics():
        """获取V站热门主题"""
        url = 'https://v2ex.com/?tab=hot'
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        contents = []
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
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
        """主方法"""
        contents = Action.get_v2ex_hot_topics()
        self.contents = contents[:self.count]
        if 'weixin' in self.hook:
            self.wx()
        elif 'dingtalk' in self.hook:
            self.ding()
        print(f'::set-output name=result::{self.res}')


if __name__ == '__main__':
    action = Action()
    action.run()
