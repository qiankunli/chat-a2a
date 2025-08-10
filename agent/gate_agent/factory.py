from agent.base import BaseGateAgent
from agent.gate_agent.langgraph.plan import PlanAgent
from agent.model import GateAgentConfig


def get_gate_agent(config: GateAgentConfig) -> BaseGateAgent:
    return PlanAgent('plan', config)
