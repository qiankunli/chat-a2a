from a2a.types import AgentCard

from agent.model import RemoteAgentConfig
from libs.a2a_runtime.client import AgentDesc


class A2AConfig(RemoteAgentConfig):
    card: AgentCard

    @classmethod
    def from_agent_desc(cls, agent_desc: AgentDesc) -> "A2AConfig":
        return cls(name=agent_desc.name, description=agent_desc.description, card=agent_desc.card)
