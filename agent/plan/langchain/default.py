import logging

from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.model import CallAgent, GateContext, UserRequest
from agent.plan.base import BasePlanner, PlanNext
from agent.plan.langchain.prompt import plan_next_parser, plan_system_prompt, plan_user_prompt_template
from agent.utils.langchain.message import to_lc_messages

logger = logging.getLogger(__name__)


class DefaultPlanner(BasePlanner):
    def __init__(self, llm: BaseChatModel):
        super().__init__(llm)

    # todo 支持并发返回多个step
    def plan(self, context: GateContext, user_request: UserRequest, call_agents: List[CallAgent]) -> PlanNext:
        # call_agents 表示当次agent 执行记录
        user_message = plan_user_prompt_template.render(
            agents=context.agent_configs,
            call_agents=call_agents,
            agent_history=context.agent_history,
            user_query=user_request.query,
        )
        planner_prompt = ChatPromptTemplate.from_messages([
            ('system', plan_system_prompt),
            MessagesPlaceholder('chat_history', optional=True),
            ('human', user_message),
        ])
        chat_history = to_lc_messages(context.chat_history)
        chain = planner_prompt | self.llm | plan_next_parser
        inputs = {'format_instructions': plan_next_parser.get_format_instructions()}
        if chat_history:
            inputs['chat_history'] = chat_history
        result = chain.invoke(inputs)
        logger.info(f'call agent_name: {result.agent_name} with query {result.query}, end {result.end}')
        return result
