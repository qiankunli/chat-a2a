from jinja2 import Template

report_system_prompt = """你是一名总结工具，负责根据用户问题和各 Agent 的执行记录，生成一个完整、流畅、准确的最终回答。

输入包括：
1. 用户当前的问题
2. 当前问题的 Agent 执行记录
3. 用户的历史聊天记录（可选）

分析步骤：
1. 综合所有 Agent 的回答内容。
2. 去掉重复、无关或冲突的部分。
3. 保证逻辑清晰，语言自然，信息准确。
4. 若信息不足以完整回答，则明确指出缺失内容。

输出要求：
- 直接给出最终的自然语言回答
"""

report_user_prompt_template = Template("""
{%- if call_agents is not none and call_agents|length>0%}
## Agent执行记录
{%- for call_agent in call_agents %}
- 调用Agent：{{ call_agent.agent_name }}
  问题：{{ call_agent.query }}
  回答：{{ call_agent.answer }}
  原因：{{ call_agent.reason }}
{% endfor %}
{% endif %}

用户问题：{{ user_query }}
""")