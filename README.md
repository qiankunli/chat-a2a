# 简介

chat-a2a 是一个支持a2a协议的multiagent 问答服务。 项目特点

1. 原生multiagent 理念来设计问答系统，区分gate_agent和agent
    1. gate_agent 负责接收用户问题，将问题分发给不同的agent
    2. agent回答用户问题，分为local agent 和remote agent 两种形式
2. 基于A2A来访问remote Agent，与[a2a-runtime](https://github.com/qiankunli/a2a-runtime) 配合使用

<img src="assets/overview.png" alt="overview"/>

# 特性

## 原生multiagent 理念

原生multiagent 体现在

1. 项目默认采用plan ==> remote agent ==> plan ==> ... ==> report 链路来回答问题
2. 数据库message表负责存储问答记录，除了用户问题和最终回答外（有report 组件提供），额外记录了`<子问题、agent回答>`

## 支持反问

支持反问相关设计如下

1. 子agent 反问通过input_required 来表达，这也是a2a推荐的方式
2. 反问场景下，用户两次输入的问题属于同一个task_id(a2a中的概念)
3. 用户/前端和gate_agent 并不感知某条agent 输出是否是反问，而是根据message表跟踪agent 执行记录。这样做可以让gate_agent
   无需引入类似langgraph checkpoint机制 ，更灵活一些。

# 联系我

项目仍不完善，欢迎共创
<img src="assets/wechat-qrcode.jpg" alt="WeChat QR Code" width="350" height="350"/>