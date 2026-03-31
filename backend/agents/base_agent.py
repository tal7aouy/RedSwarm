from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json
from core.logger import setup_logger

logger = setup_logger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentPersona(Enum):
    APT28 = "apt28"
    APT29 = "apt29"
    LAZARUS = "lazarus"
    SCRIPT_KIDDIE = "script_kiddie"
    INSIDER = "insider"
    RANSOMWARE = "ransomware"
    GENERIC = "generic"


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        persona: AgentPersona = AgentPersona.GENERIC,
        llm_client: Any = None,
        memory_size: int = 1000
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.persona = persona
        self.llm_client = llm_client
        self.status = AgentStatus.IDLE
        self.memory: List[Dict[str, Any]] = []
        self.memory_size = memory_size
        self.actions_taken: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        
        logger.info(f"Initialized {self.agent_type} agent {self.agent_id} with persona {self.persona.value}")
    
    def add_memory(self, memory: Dict[str, Any]):
        memory["timestamp"] = datetime.utcnow().isoformat()
        self.memory.append(memory)
        
        if len(self.memory) > self.memory_size:
            self.memory = self.memory[-self.memory_size:]
        
        logger.debug(f"Agent {self.agent_id} added memory: {memory.get('type', 'unknown')}")
    
    def get_recent_memory(self, count: int = 10) -> List[Dict[str, Any]]:
        return self.memory[-count:]
    
    def record_action(self, action: Dict[str, Any], llm_reasoning: str = None):
        action["timestamp"] = datetime.utcnow().isoformat()
        action["agent_id"] = self.agent_id
        if llm_reasoning:
            action["llm_reasoning"] = llm_reasoning
        self.actions_taken.append(action)
        
        self.add_memory({
            "type": "action",
            "action": action
        })
        
        logger.info(f"Agent {self.agent_id} recorded action: {action.get('action_type', 'unknown')}")
    
    def update_status(self, status: AgentStatus):
        old_status = self.status
        self.status = status
        logger.info(f"Agent {self.agent_id} status: {old_status.value} -> {status.value}")
    
    def get_persona_traits(self) -> Dict[str, Any]:
        persona_traits = {
            AgentPersona.APT28: {
                "sophistication": "high",
                "stealth": "high",
                "patience": "high",
                "tools": ["custom_malware", "zero_days", "spear_phishing"],
                "tactics": ["reconnaissance", "lateral_movement", "persistence"],
                "behavior": "methodical and patient, focuses on long-term access"
            },
            AgentPersona.APT29: {
                "sophistication": "very_high",
                "stealth": "very_high",
                "patience": "very_high",
                "tools": ["custom_backdoors", "living_off_the_land", "supply_chain"],
                "tactics": ["advanced_persistence", "data_exfiltration", "covering_tracks"],
                "behavior": "extremely stealthy, uses legitimate tools, minimal footprint"
            },
            AgentPersona.LAZARUS: {
                "sophistication": "high",
                "stealth": "medium",
                "patience": "medium",
                "tools": ["custom_malware", "destructive_payloads", "cryptocurrency_theft"],
                "tactics": ["initial_access", "privilege_escalation", "impact"],
                "behavior": "financially motivated, willing to be destructive"
            },
            AgentPersona.SCRIPT_KIDDIE: {
                "sophistication": "low",
                "stealth": "low",
                "patience": "low",
                "tools": ["public_exploits", "automated_scanners", "default_credentials"],
                "tactics": ["scanning", "exploitation", "defacement"],
                "behavior": "noisy and impatient, uses automated tools, makes mistakes"
            },
            AgentPersona.INSIDER: {
                "sophistication": "medium",
                "stealth": "high",
                "patience": "high",
                "tools": ["legitimate_access", "data_theft", "sabotage"],
                "tactics": ["collection", "exfiltration", "impact"],
                "behavior": "has legitimate access, knows internal systems, careful to avoid detection"
            },
            AgentPersona.RANSOMWARE: {
                "sophistication": "medium",
                "stealth": "medium",
                "patience": "low",
                "tools": ["encryption", "data_exfiltration", "double_extortion"],
                "tactics": ["initial_access", "lateral_movement", "impact"],
                "behavior": "focused on encryption and extortion, moves quickly"
            },
            AgentPersona.GENERIC: {
                "sophistication": "medium",
                "stealth": "medium",
                "patience": "medium",
                "tools": ["common_tools", "public_exploits"],
                "tactics": ["standard_attack_chain"],
                "behavior": "balanced approach, uses common techniques"
            }
        }
        
        return persona_traits.get(self.persona, persona_traits[AgentPersona.GENERIC])
    
    @abstractmethod
    async def plan(self, target: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def adapt(self, feedback: Dict[str, Any]) -> None:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "persona": self.persona.value,
            "status": self.status.value,
            "memory_count": len(self.memory),
            "actions_count": len(self.actions_taken),
            "created_at": self.created_at.isoformat(),
            "persona_traits": self.get_persona_traits()
        }
