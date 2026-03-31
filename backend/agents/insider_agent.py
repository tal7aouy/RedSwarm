from typing import Dict, List, Any
from agents.base_agent import BaseAgent, AgentStatus, AgentPersona
from core.logger import setup_logger
from core.agent_prompts import INSIDER_SYSTEM_PROMPT, EXECUTE_USER_PROMPT, ADAPT_USER_PROMPT
import asyncio
import json

logger = setup_logger(__name__)


class InsiderAgent(BaseAgent):
    def __init__(self, agent_id: str, persona: AgentPersona = AgentPersona.INSIDER, llm_client: Any = None):
        super().__init__(agent_id, "insider", persona, llm_client)
        self.legitimate_access: Dict[str, Any] = {}
        self.internal_knowledge: List[Dict[str, Any]] = []
        self.sabotage_actions: List[Dict[str, Any]] = []
    
    def _get_system_prompt(self) -> str:
        traits = self.get_persona_traits()
        return INSIDER_SYSTEM_PROMPT.format(
            persona_name=self.persona.value,
            persona_traits=json.dumps(traits, indent=2)
        )
    
    async def plan(self, target: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        self.update_status(AgentStatus.THINKING)
        
        persona_traits = self.get_persona_traits()
        
        plan = []
        
        plan.append({
            "action_type": "abuse_legitimate_access",
            "description": "Use legitimate credentials to access sensitive systems",
            "mitre_tactic": "TA0001",
            "mitre_technique": "T1078",
            "priority": 1
        })
        
        plan.append({
            "action_type": "internal_reconnaissance",
            "description": "Map internal systems using insider knowledge",
            "mitre_tactic": "TA0007",
            "mitre_technique": "T1087",
            "priority": 2
        })
        
        plan.append({
            "action_type": "access_sensitive_data",
            "description": "Access sensitive data using legitimate permissions",
            "mitre_tactic": "TA0009",
            "mitre_technique": "T1005",
            "priority": 3
        })
        
        plan.append({
            "action_type": "data_staging",
            "description": "Stage data for exfiltration",
            "mitre_tactic": "TA0009",
            "mitre_technique": "T1074",
            "priority": 4
        })
        
        plan.append({
            "action_type": "exfiltrate_via_legitimate_channel",
            "description": "Exfiltrate data through normal business channels",
            "mitre_tactic": "TA0010",
            "mitre_technique": "T1567",
            "priority": 5
        })
        
        if "sabotage" in persona_traits.get("tools", []):
            plan.append({
                "action_type": "sabotage_systems",
                "description": "Sabotage critical systems",
                "mitre_tactic": "TA0040",
                "mitre_technique": "T1485",
                "priority": 6
            })
        
        self.add_memory({
            "type": "plan",
            "plan": plan,
            "target": target
        })
        
        logger.info(f"InsiderAgent {self.agent_id} created plan with {len(plan)} actions")
        return plan
    
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status(AgentStatus.EXECUTING)
        
        action_type = action.get("action_type")
        
        if self.llm_client and self.llm_client.is_available:
            result, llm_reasoning = await self._llm_execute(action, context)
        else:
            if action_type == "abuse_legitimate_access":
                result = await self._abuse_legitimate_access(context)
            elif action_type == "internal_reconnaissance":
                result = await self._internal_reconnaissance(context)
            elif action_type == "access_sensitive_data":
                result = await self._access_sensitive_data(context)
            elif action_type == "data_staging":
                result = await self._data_staging(context)
            elif action_type == "exfiltrate_via_legitimate_channel":
                result = await self._exfiltrate_via_legitimate_channel(context)
            elif action_type == "sabotage_systems":
                result = await self._sabotage_systems(context)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action type: {action_type}"
                }
            llm_reasoning = None
        
        self.record_action({
            "action_type": action_type,
            "result": result,
            "mitre_tactic": action.get("mitre_tactic"),
            "mitre_technique": action.get("mitre_technique")
        }, llm_reasoning)
        
        self.update_status(AgentStatus.IDLE)
        return result
    
    async def _llm_execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        from core.agent_prompts import EXECUTE_USER_PROMPT
        prompt = EXECUTE_USER_PROMPT.format(
            action_type=action.get("action_type"),
            action_description=action.get("description", ""),
            target=json.dumps(context.get("target", {})),
            context=json.dumps({k: str(v)[:300] for k, v in context.items()})
        )
        raw = await self.llm_client.generate_json(self._get_system_prompt(), prompt, max_tokens=2048)
        try:
            result = json.loads(raw)
            if isinstance(result, dict):
                result.setdefault("success", True)
                result.setdefault("description", f"Executed {action.get('action_type')}")
                return result, raw
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"InsiderAgent {self.agent_id}: LLM execute parse failed, using fallback")
        
        # Fallback to original logic
        action_type = action.get("action_type")
        if action_type == "abuse_legitimate_access":
            fallback_result = await self._abuse_legitimate_access(context)
        elif action_type == "internal_reconnaissance":
            fallback_result = await self._internal_reconnaissance(context)
        elif action_type == "access_sensitive_data":
            fallback_result = await self._access_sensitive_data(context)
        elif action_type == "data_staging":
            fallback_result = await self._data_staging(context)
        elif action_type == "exfiltrate_via_legitimate_channel":
            fallback_result = await self._exfiltrate_via_legitimate_channel(context)
        elif action_type == "sabotage_systems":
            fallback_result = await self._sabotage_systems(context)
        else:
            fallback_result = {
                "success": False,
                "error": f"Unknown action type: {action_type}"
            }
        return fallback_result, None
    
    async def _abuse_legitimate_access(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        self.legitimate_access = {
            "username": "john.doe",
            "role": "senior_developer",
            "permissions": ["read_source_code", "access_databases", "deploy_applications"],
            "access_level": "high"
        }
        
        self.add_memory({
            "type": "success",
            "category": "legitimate_access",
            "access": self.legitimate_access
        })
        
        return {
            "success": True,
            "access": self.legitimate_access,
            "description": "Using legitimate access as senior developer"
        }
    
    async def _internal_reconnaissance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        internal_systems = [
            {"name": "HR Database", "location": "hr-db.internal", "sensitivity": "high"},
            {"name": "Financial System", "location": "finance.internal", "sensitivity": "critical"},
            {"name": "Customer Database", "location": "customers-db.internal", "sensitivity": "critical"},
            {"name": "Source Code Repository", "location": "git.internal", "sensitivity": "high"}
        ]
        
        self.internal_knowledge.extend(internal_systems)
        
        self.add_memory({
            "type": "discovery",
            "category": "internal_systems",
            "systems": internal_systems
        })
        
        return {
            "success": True,
            "systems": internal_systems,
            "description": f"Mapped {len(internal_systems)} internal systems using insider knowledge"
        }
    
    async def _access_sensitive_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        sensitive_data = {
            "customer_records": 150000,
            "financial_data": "Q4_2024_financials.xlsx",
            "source_code": "proprietary_algorithm.py",
            "credentials": "admin_passwords.txt"
        }
        
        self.add_memory({
            "type": "success",
            "category": "data_access",
            "data": sensitive_data
        })
        
        return {
            "success": True,
            "data_accessed": sensitive_data,
            "description": "Accessed sensitive data using legitimate permissions"
        }
    
    async def _data_staging(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        staging = {
            "location": "personal_cloud_storage",
            "method": "legitimate_file_sharing",
            "size": "5.2GB",
            "encrypted": True
        }
        
        self.add_memory({
            "type": "success",
            "category": "data_staging",
            "staging": staging
        })
        
        return {
            "success": True,
            "staging": staging,
            "description": "Data staged in personal cloud storage"
        }
    
    async def _exfiltrate_via_legitimate_channel(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        exfiltration = {
            "method": "corporate_email",
            "destination": "personal_email@gmail.com",
            "data_size": "5.2GB",
            "appears_legitimate": True,
            "detection_risk": "low"
        }
        
        self.add_memory({
            "type": "success",
            "category": "exfiltration",
            "exfiltration": exfiltration
        })
        
        return {
            "success": True,
            "exfiltration": exfiltration,
            "description": "Data exfiltrated via legitimate business channel"
        }
    
    async def _sabotage_systems(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        sabotage = {
            "target": "production_database",
            "action": "delete_critical_tables",
            "impact": "high",
            "reversible": False
        }
        
        self.sabotage_actions.append(sabotage)
        
        self.add_memory({
            "type": "success",
            "category": "sabotage",
            "sabotage": sabotage
        })
        
        return {
            "success": True,
            "sabotage": sabotage,
            "description": "Critical systems sabotaged"
        }
    
    async def adapt(self, feedback: Dict[str, Any]) -> None:
        if self.llm_client and self.llm_client.is_available and feedback.get("defense_injected"):
            defense = feedback.get("defense", {})
            prompt = ADAPT_USER_PROMPT.format(
                defense_type=defense.get("type", "unknown"),
                defense_details=json.dumps(defense),
                previous_actions=[a.get("action_type") for a in self.actions_taken[-5:]],
                context="Insider threat phase"
            )
            raw = await self.llm_client.generate_json(self._get_system_prompt(), prompt, max_tokens=1024)
            try:
                adaptation = json.loads(raw)
                self.add_memory({"type": "adaptation", "strategy": adaptation})
                logger.info(f"InsiderAgent {self.agent_id} adapted: {adaptation.get('adaptation_strategy', 'unknown')}")
                return
            except (json.JSONDecodeError, TypeError):
                pass
        
        if feedback.get("blocked") or feedback.get("suspicious_activity_flagged"):
            self.add_memory({"type": "adaptation", "reason": "activity_flagged", "action": "slow_down_and_act_more_normal"})
            logger.info(f"InsiderAgent {self.agent_id} activity flagged, slowing down")
        if feedback.get("access_revoked"):
            self.add_memory({"type": "adaptation", "reason": "access_revoked", "action": "use_cached_data_and_exit"})
            logger.info(f"InsiderAgent {self.agent_id} access revoked, using cached data")
