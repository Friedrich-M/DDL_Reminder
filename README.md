# DDL_Reminder
DDL提醒小助手（钉钉智能机器人版）

源码来自[Dimlitter](https://github.com/Dimlitter)同学

对代码中的部分bug进行修正，增加了部分内容，并更新完整步骤实现

## 简介

- 模拟学在浙大平台登录

- 通过发送简单的GET请求获取DDL信息

- github action 部署，无需服务器

## 使用方法

1、fork本项目

2、配置github secret

3、开启github action推送

## 参数配置

> 必须配置的内容

```bash
ZJU_USERNAME : 'username',
ZJU_PASSWORD : 'password',
```

> 可选配置内容

<font size="3">钉钉机器人的推送</font>

```bash
'DD_BOT_SECRET': '',      # 钉钉机器人的 DD_BOT_SECRET，加签密钥
'DD_BOT_TOKEN' : '',      # 钉钉机器人的 DD_BOT_TOKEN, access_token后一段
```

## 自定义运行时间

> <font size="3">修改`.github/workflows/run.yml`文件中的自定义运行时间</font>

```yml
watch:
    types: [ started ]
  schedule:
    - cron: 45 22 * * *
```

- 注意，cron表达式时间为UTC时间，与北京时间相差八小时



## 添加钉钉智能机器人
1. 用手机钉钉用面对面建群的方式建一个新群
2. 用电脑钉钉打开群设置，找到<智能群助手>

<img src="https://user-images.githubusercontent.com/85838942/167482748-d3ce398a-9c46-4afc-aa98-5d1cd4601f35.png" width=30% height=30%>

3. 添加群机器人，选择自定义，名字任取
<img src="https://user-images.githubusercontent.com/85838942/167483147-a096ac03-a23d-4b19-8396-3c55a2122706.png" width=30% height=30%>

4. 钉钉机器人的 DD_BOT_TOKEN, access_token后一段
<img src="https://user-images.githubusercontent.com/85838942/167483523-e7fa719a-b89f-4336-b643-adf66e4754a5.png" width=30% height=30%>

5. 钉钉机器人的 DD_BOT_SECRET，加签密钥
<img src="https://user-images.githubusercontent.com/85838942/167483696-5dcf4fc9-af8d-41ac-8e88-3e589ca962ae.png" width=30% height=30%>
