from agent.base import BaseAgent
from agent.model import RemoteAgentConfig
from agent.remote_agent.a2a.default import DefaultAgent


def get_remote_agent(config: RemoteAgentConfig) -> BaseAgent:
    # todo 后续避免每次都初始化
    return DefaultAgent(config)
