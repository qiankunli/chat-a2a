import logging

from typing import Any, Dict, List

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langgraph.runtime import Runtime
from langgraph.types import Command

from agent.gate_agent.langgraph.base import BaseLGGateAgent, ContextSchema
from agent.gate_agent.langgraph.event import (
    dispatch_agent_end_event,
    dispatch_answer_end_event,
    dispatch_answer_event,
    dispatch_header_event,
    dispatch_message_event, dispatch_input_required_event,
)
from agent.model import CallAgent, GateAgentConfig, GateContext, MessageRole, SendMessage, UserRequest, MessageType
from agent.plan.langchain.default import DefaultPlanner
from agent.remote_agent.factory import get_remote_agent
from agent.reporter.langchain.default import DefaultReporter

logger = logging.getLogger(__name__)


class State(MessagesState):
    user_request: UserRequest
    selected_agent: str
    call_agent_query: str
    call_agents: List[CallAgent]
    call_agent_nums: int


class PlanAgent(BaseLGGateAgent):

    def __init__(self, name: str, config: GateAgentConfig):
        super().__init__(name, config)
        self.plan = DefaultPlanner(llm=config.llm)
        self.reporter = DefaultReporter(llm=config.llm)
        self.chain = self._build_graph()

    def _build_input(self, gate_context: GateContext,
                     user_request: UserRequest, ) -> Dict[str, Any]:
        return {"user_request": user_request, 'call_agents': [], 'call_agent_nums': 0}

    def _build_graph(self):
        async def plan_node(state: State, runtime: Runtime[ContextSchema], config: RunnableConfig):
            call_agents = state['call_agents']
            plan = self.plan.plan(runtime.context['gate_context'], state['user_request'], call_agents)
            if plan.end:
                return Command(
                    update={
                        'call_agents': call_agents + [
                            CallAgent(name=plan.agent_name, query=plan.query, reason=plan.reason)],
                    },
                    goto='report',
                )
            call_agent_nums = state['call_agent_nums']
            if call_agent_nums > 3:
                return Command(
                    update={
                        'call_agents': call_agents + [
                            CallAgent(name='无', query=plan.query, reason='调用Agent超过3轮，停止调用')],
                    },
                    goto='report',
                )
            return Command(
                update={
                    'selected_agent': plan.agent_name,
                    'call_agent_query': plan.query,
                    'call_agent_nums': call_agent_nums + 1,
                },
                goto='call_agent',
            )

        async def call_agent_node(state: State, runtime: Runtime[ContextSchema], config: RunnableConfig):
            selected_agent = state['selected_agent']
            call_agent_query = state['call_agent_query']
            gate_context = runtime.context['gate_context']
            agent = get_remote_agent(gate_context.get_agent_config(selected_agent))
            message = SendMessage(content=call_agent_query, role=MessageRole.USER)
            await dispatch_header_event(self.name, call_agent_query, config)
            response = agent.arun(gate_context, message)
            answer = ''
            async for resp in response:
                if resp.type == MessageType.INPUT_REQUIRED:
                    await dispatch_input_required_event(selected_agent, resp.content, config)
                    return Command(goto=END, )
                chunk = resp.content
                await dispatch_message_event(selected_agent, chunk, config)
                answer += chunk

            logger.info(f'call agent {selected_agent} with query {call_agent_query} get answer {answer}')
            await dispatch_agent_end_event(selected_agent, config)
            return Command(
                update={
                    'call_agents': state['call_agents'] + [
                        CallAgent(name=selected_agent, query=call_agent_query, answer=answer)],
                },
                goto='plan',
            )

        async def report_node(state: State, runtime: Runtime[ContextSchema], config: RunnableConfig):
            call_agents = state['call_agents']
            gate_context = runtime.context['gate_context']
            response = self.reporter.report(gate_context, state['user_request'], call_agents)
            answer = ''
            async for chunk in response:
                await dispatch_answer_event(chunk, config)
                answer += chunk
            await dispatch_answer_end_event(config)
            return Command(
                goto=END,
            )

        workflow = StateGraph(State)
        workflow.add_node('plan', plan_node)
        workflow.add_node('call_agent', call_agent_node)
        workflow.add_node('report', report_node)
        workflow.add_edge(START, 'plan')

        return workflow.compile()
