# 简介

chat-a2a 是一个支持a2a协议的，基于multiagent 设计的问答服务。 

<img src="assets/overview.png" alt="overview"/>

项目特点
1. 默认采用multiagent 回答用户问题，即一个问题至少经过一个plan agent和一个execute agent。
2. 多个agent之间的关系有多种范式，本项目默认采用集中式编排范式，由主控 Agent（Planner）负责接收用户输入、拆分任务、分配给子 Agent 执行。
   1. 示例链路 query ==> plan ==> agent1 ==> plan ==> agent2 ==> ... ==> report 
3. 在工程上采用plan agent 与 execute agent 分离的设计，plan agent由本项目负责，execute agent的管理由[a2a-runtime](https://github.com/qiankunli/a2a-runtime) 负责，两个项目之间通过a2a协议通信。
   1. chat-a2a 只负责通过gate-agent(plan) 编排remote agent回答问题（也可以在chat-a2a中实现local agent），自身并不负责直接回答问题。
   2. chat-a2a负责维护会话、用户（还未加）、聊天等数据，remote agent 只负责根据输入给出输出即可（可以考虑接入mcp），理论上无需再访问db等存储。
4. agent问答记录直接存在message表中，地位与用户问题、最终答案相同。

   |id|conv_id| intention_id|role|type|content|agent|
   |---|---|------------|---|---|---|---|
   |1|conv1| intention1 |user||天气如何||
   |2|conv1| intention1 |agent|query|天气如何|plan|
   |3|conv1| intention1 |agent|input_required|您问到哪里的天气|weather|
   |4|conv1| intention1 |user||上海||
   |5|conv1| intention1 |agent|query|上海天气如何|plan|
   |6|conv1| intention1 |agent|answer|上海天气很热|weather|
   |7|conv1| intention1 |assistant||上海天气很热||


# 特性

## 意图

关于问答
1. 最小粒度的概念是message_id
2. 最大粒度的概念是conversation_id
两者之间，一个较为中间粒度的概念是意图/intention_id(本来想叫task_id，但不想跟a2a 中的task_id对应)

考虑到问答链路， 以是否有人工参与，分为以下场景
1. 简单问答，无需人工，plan 调度几次agent 即可回答
  1. plan ==> agent ==> report
  2. plan ==> agent1 ==> plan => agent2 ==> report 
  3. plan ==> agent1 ==> plan ==> agent1 ==> report。（假设agent1 是一个检索agent，则在一次问答时可能被多次调用）
2. 复杂问答
  1. plan ==> agent1(input_required) ==> user ==> plan ==> agent1 ==> report 
  2. plan ==> agent1(input_required) ==> user ==> plan ==> agent1 ==> plan ==> agent2 ==> report

这些message 在db 里共用一个intention_id，主要用于在带有input_required场景下第二次user 进入plan时， 为plan恢复plan的上下文。

## 关于反问的处理

支持反问相关设计如下

1. local/remote agent 反问通过input_required 来表达，这也是a2a推荐的方式
2. 反问场景下，用户两次输入的问题属于同一个intention_id
3. 用户/前端和gate_agent 并不感知某条agent 输出是否是反问，而是根据message表跟踪agent 执行记录。这样做可以让gate_agent
   无需引入类似langgraph checkpoint机制 ，更灵活一些。

如果用户在反问场景下，不回应agent返回而是直接输入新问题，则仍沿用之前的task_id 会有问题，后续会继续优化。

```
用户：天气如何
AI：您问哪里的天气？
用户：曹操是谁
AI：xx
```

# 运行

1. 选择一个db，创建chat-a2a 数据库
2. 运行migrations/up/v1.0.0.sql 创建数据库表
3. `cp .env.example .env`
4. 配置.env 文件，主要包括db 连接信息、llm 模型信息
5. 安装python 依赖
    ```
    poetry install
    ```
6. 启动a2a-runtime
7. 运行chat-a2a
    ```
    poetry run python -m main
    # 或配置venv 后运行
    python main.py
    ```

# 联系我

项目仍不完善，欢迎共创

<img src="assets/wechat-qrcode.jpg" alt="WeChat QR Code" width="350" height="450"/>