# prompts/planner_prompt.py
from jinja2 import Template
from langchain_core.output_parsers import PydanticOutputParser

from agent.plan.base import PlanNext

# 结构化输出解析器
plan_next_parser = PydanticOutputParser(pydantic_object=PlanNext)

plan_system_prompt = """你是一名智能任务规划器，负责分析用户问题，并将其分配给最合适的 Agent 处理。  
输入包括：
1. 用户当前的问题
2. 可用 Agent 列表（包含 name 和 description）
3. 当前问题的 Agent 执行记录
4. 用户的历史聊天记录

分析步骤：
1. 根据 “Agent 执行记录” 判断用户的问题是否已被充分回答。
   - 若已充分回答，则结束任务。
2. 若未充分回答，明确本次需要解决的“待解决问题”。
3. 从 “Agent 列表” 中选择最能解决该“待解决问题”的 Agent。
4. 如果“待解决问题”与任何 Agent 功能描述均不匹配，则结束任务，并将 Agent 名称设为 "无"。

输出要求：
- 严格使用 JSON 格式
- 字段说明：
  1. `agent_name`: 下一步要调用的 Agent 名称
  2. `query`: 下一步要调用该 Agent 时的查询语句（使用主谓宾完整表达）
  3. `end`: 是否结束任务（true/false）
  4. `reason`: 选择该 Agent 的原因（可选，尽量简短）

{format_instructions}
"""
plan_user_prompt_template = Template("""
{%- if agents is not none and agents|length>0%}
## Agent列表 
{%- for agent in agents%}
- 名称：{{agent.name}}
  功能描述：{{agent.description}}
{% endfor %}
{% endif %}

{%- if agent_history is not none and agent_history|length>0%}
## 上轮Agent执行记录
{%- for agent_message in agent_history%}
- 调用Agent：{{agent_message.agent}}
  消息类型：{{agent_message.type}}
  消息内容：{{agent_message.content}}
{% endfor %}
{% endif %}

{%- if call_agents is not none and call_agents|length>0%}
## 本轮Agent执行记录
{%- for call_agent in call_agents%}
- 调用Agent：{{call_agent.agent_name}}
  问题：{{call_agent.query}}
  回答：{{call_agent.answer}}
  原因：{{call_agent.reason}}
{% endfor %}
{% endif %}

用户问题：{{user_query}}
""")
