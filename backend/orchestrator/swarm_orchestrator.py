from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import uuid
from core.logger import setup_logger
from core.llm_client import get_llm_client
from agents import ReconAgent, ExploitAgent, PostExploitAgent, InsiderAgent, AgentPersona
from orchestrator.attack_graph import AttackGraph
from orchestrator.god_mode import GodModeManager

logger = setup_logger(__name__)


class SwarmOrchestrator:
    def __init__(
        self,
        target: str,
        scenario: Optional[str] = None,
        agent_types: Optional[List[str]] = None,
        personas: Optional[Dict[str, str]] = None,
        llm_client: Any = None
    ):
        self.simulation_id = str(uuid.uuid4())
        self.target = target
        self.scenario = scenario
        self.llm_client = llm_client or get_llm_client()
        
        self.agents: Dict[str, Any] = {}
        self.attack_graph = AttackGraph(self.simulation_id)
        self.god_mode = GodModeManager(self.simulation_id)
        
        self.status = "initialized"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        self.context: Dict[str, Any] = {
            "target": {"ip": target},
            "vulnerabilities": [],
            "access": [],
            "discovered_assets": [],
            "injections": []
        }
        
        self._initialize_agents(agent_types or ["recon", "exploit", "post_exploit"], personas or {})
        
        logger.info(f"SwarmOrchestrator initialized for simulation {self.simulation_id}")
    
    def _initialize_agents(self, agent_types: List[str], personas: Dict[str, str]):
        for agent_type in agent_types:
            agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
            persona_str = personas.get(agent_type, "generic")
            persona = AgentPersona[persona_str.upper()] if persona_str.upper() in AgentPersona.__members__ else AgentPersona.GENERIC
            
            if agent_type == "recon":
                agent = ReconAgent(agent_id, persona, self.llm_client)
            elif agent_type == "exploit":
                agent = ExploitAgent(agent_id, persona, self.llm_client)
            elif agent_type == "post_exploit":
                agent = PostExploitAgent(agent_id, persona, self.llm_client)
            elif agent_type == "insider":
                agent = InsiderAgent(agent_id, persona, self.llm_client)
            else:
                logger.warning(f"Unknown agent type: {agent_type}")
                continue
            
            self.agents[agent_id] = agent
            self.attack_graph.add_agent(agent_id, agent_type)
            
            logger.info(f"Initialized {agent_type} agent: {agent_id}")
    
    async def execute(self) -> Dict[str, Any]:
        self.status = "running"
        self.start_time = datetime.utcnow()
        
        logger.info(f"Starting simulation {self.simulation_id}")
        
        try:
            await self._run_recon_phase()
            
            await self._run_exploit_phase()
            
            await self._run_post_exploit_phase()
            
            self.status = "completed"
            self.end_time = datetime.utcnow()
            
            logger.info(f"Simulation {self.simulation_id} completed successfully")
            
            return self.generate_report()
            
        except Exception as e:
            self.status = "failed"
            self.end_time = datetime.utcnow()
            logger.error(f"Simulation {self.simulation_id} failed: {e}", exc_info=True)
            raise
    
    async def _run_recon_phase(self):
        logger.info("Starting reconnaissance phase")
        
        recon_agents = [agent for agent_id, agent in self.agents.items() if agent.agent_type == "recon"]
        
        for agent in recon_agents:
            plan = await agent.plan(self.context["target"], self.context)
            
            for action in plan:
                if self.god_mode.is_blocked(action):
                    logger.info(f"Action blocked by God Mode: {action['action_type']}")
                    await agent.adapt({"blocked": True})
                    continue
                
                result = await agent.execute(action, self.context)
                
                self.attack_graph.add_action(
                    agent.agent_id,
                    action["action_type"],
                    result,
                    action.get("mitre_tactic"),
                    action.get("mitre_technique")
                )
                
                if result.get("success"):
                    self._update_context_from_recon(result)
                
                await asyncio.sleep(0.1)
        
        logger.info(f"Reconnaissance phase completed. Found {len(self.context['vulnerabilities'])} vulnerabilities")
    
    async def _run_exploit_phase(self):
        logger.info("Starting exploitation phase")
        
        if not self.context["vulnerabilities"]:
            logger.warning("No vulnerabilities found, skipping exploitation phase")
            return
        
        exploit_agents = [agent for agent_id, agent in self.agents.items() if agent.agent_type == "exploit"]
        
        for agent in exploit_agents:
            plan = await agent.plan(self.context["target"], self.context)
            
            for action in plan:
                if self.god_mode.is_blocked(action):
                    logger.info(f"Action blocked by God Mode: {action['action_type']}")
                    await agent.adapt({"blocked": True})
                    continue
                
                result = await agent.execute(action, self.context)
                
                self.attack_graph.add_action(
                    agent.agent_id,
                    action["action_type"],
                    result,
                    action.get("mitre_tactic"),
                    action.get("mitre_technique")
                )
                
                if result.get("success") and result.get("access"):
                    self.context["access"].append(result["access"])
                
                await asyncio.sleep(0.1)
        
        logger.info(f"Exploitation phase completed. Gained {len(self.context['access'])} access points")
    
    async def _run_post_exploit_phase(self):
        logger.info("Starting post-exploitation phase")
        
        if not self.context["access"]:
            logger.warning("No access gained, skipping post-exploitation phase")
            return
        
        post_exploit_agents = [agent for agent_id, agent in self.agents.items() 
                               if agent.agent_type == "post_exploit" or agent.agent_type == "insider"]
        
        for agent in post_exploit_agents:
            plan = await agent.plan(self.context["target"], self.context)
            
            for action in plan:
                if self.god_mode.is_blocked(action):
                    logger.info(f"Action blocked by God Mode: {action['action_type']}")
                    await agent.adapt({"blocked": True})
                    continue
                
                result = await agent.execute(action, self.context)
                
                self.attack_graph.add_action(
                    agent.agent_id,
                    action["action_type"],
                    result,
                    action.get("mitre_tactic"),
                    action.get("mitre_technique")
                )
                
                await asyncio.sleep(0.1)
        
        logger.info("Post-exploitation phase completed")
    
    def _update_context_from_recon(self, result: Dict[str, Any]):
        if "vulnerabilities" in result:
            self.context["vulnerabilities"].extend(result["vulnerabilities"])
        
        if "open_ports" in result:
            self.context["discovered_assets"].extend(result["open_ports"])
        
        if "services" in result:
            self.context["discovered_assets"].extend(result["services"])
    
    def inject_defense(self, defense: Dict[str, Any]):
        self.god_mode.inject_defense(defense)
        self.context["injections"].append(defense)
        
        logger.info(f"Defense injected: {defense.get('type')}")
        
        for agent in self.agents.values():
            asyncio.create_task(agent.adapt({"defense_injected": True, "defense": defense}))
    
    def generate_report(self, format: str = "json") -> Dict[str, Any]:
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
        else:
            duration = 0
        
        report = {
            "simulation_id": self.simulation_id,
            "target": self.target,
            "scenario": self.scenario,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "agents": {
                agent_id: agent.to_dict() 
                for agent_id, agent in self.agents.items()
            },
            "attack_graph": self.attack_graph.to_dict(),
            "summary": {
                "vulnerabilities_found": len(self.context["vulnerabilities"]),
                "access_gained": len(self.context["access"]),
                "total_actions": sum(len(agent.actions_taken) for agent in self.agents.values()),
                "successful_actions": sum(
                    1 for agent in self.agents.values() 
                    for action in agent.actions_taken 
                    if action.get("result", {}).get("success")
                ),
                "god_mode_injections": len(self.context["injections"])
            },
            "mitre_attack_mapping": self.attack_graph.get_mitre_mapping()
        }
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "target": self.target,
            "scenario": self.scenario,
            "status": self.status,
            "agents": {
                agent_id: {
                    "type": agent.agent_type,
                    "agent_type": agent.agent_type,
                    "persona": agent.persona.value,
                    "status": agent.status.value,
                    "actions_count": len(agent.actions_taken),
                }
                for agent_id, agent in self.agents.items()
            },
        }
