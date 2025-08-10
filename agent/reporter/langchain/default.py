from typing import AsyncGenerator, List

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.model import CallAgent, GateContext, UserRequest
from agent.reporter.base import BaseReporter
from agent.reporter.langchain.prompt import report_system_prompt, report_user_prompt_template
from agent.utils.langchain.message import to_lc_messages


class DefaultReporter(BaseReporter):
    def __init__(self, llm: BaseChatModel):
        super().__init__(llm)

    async def report(self, context: GateContext, user_request: UserRequest,
                     call_agents: List[CallAgent]) -> AsyncGenerator[str, None]:

        user_message = report_user_prompt_template.render(
            call_agents=call_agents,
            user_query=user_request.query
        )
        reporter_prompt = ChatPromptTemplate.from_messages([
            ('system', report_system_prompt),
            MessagesPlaceholder('chat_history', optional=True),
            ('human', user_message),
        ])
        chat_history = to_lc_messages(context.chat_history)

        chain = reporter_prompt | self.llm

        inputs = {}
        if chat_history:
            inputs['chat_history'] = chat_history
        async for chunk in chain.astream(inputs):
            yield chunk.content