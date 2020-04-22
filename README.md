<h1 align="center">V2EX Action</h1>

<div align="center">

[![actions status](https://github.com/yanglbme/v2ex-action/workflows/Lint/badge.svg)](https://github.com/yanglbme/v2ex-action/actions) [![release](https://img.shields.io/github/v/release/yanglbme/v2ex-action.svg)](../../releases) [![license](https://badgen.net/github/license/yanglbme/v2ex-action)](./LICENSE) [![PRs Welcome](https://badgen.net/badge/PRs/welcome/green)](../../pulls)

</div>

自动爬取 V 站热门，发送到 webhook 地址，如企业微信群机器人。可配置 workflow 的触发条件为 `schedule`，实现周期性定时爬取。

## 入参

|  参数  |  描述  |  是否必传  |  默认值  |
|---|---|---|---|
| `webhook` | Webhook 地址 | 是 | - |
| `count` | 帖子数量 | 否 | 5 |

## 完整示例
可自定义 cron 表达式。

注意 cron 是 UTC 时间，使用时请将北京时间转换为 UTC 进行配置。

```yml
name: V2ex

on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: yanglbme/v2ex-action@master
        env:
          webhook: ${{secrets.WEBHOOK}}
          count: 6
```

## 许可证
[MIT](LICENSE)