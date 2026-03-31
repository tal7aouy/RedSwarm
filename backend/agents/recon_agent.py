from typing import Dict, List, Any
from agents.base_agent import BaseAgent, AgentStatus, AgentPersona
from core.logger import setup_logger
from core.agent_prompts import RECON_SYSTEM_PROMPT, EXECUTE_USER_PROMPT, ADAPT_USER_PROMPT
import asyncio
import json
import logging
from datetime import datetime

logger = setup_logger(__name__)


class ReconAgent(BaseAgent):
    def __init__(self, agent_id: str, persona: AgentPersona = AgentPersona.GENERIC, llm_client: Any = None):
        super().__init__(agent_id, "recon", persona, llm_client)
        self.discovered_assets: List[Dict[str, Any]] = []
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.network_map: Dict[str, Any] = {}
    
    def _get_system_prompt(self) -> str:
        traits = self.get_persona_traits()
        return RECON_SYSTEM_PROMPT.format(
            persona_name=self.persona.value,
            persona_traits=json.dumps(traits, indent=2)
        )
    
    async def plan(self, target: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        self.update_status(AgentStatus.THINKING)
        persona_traits = self.get_persona_traits()
        
        if self.llm_client and self.llm_client.is_available:
            plan = await self._llm_plan(target, context, persona_traits)
        else:
            plan = self._fallback_plan(target, persona_traits)
        
        self.add_memory({"type": "plan", "plan": plan, "target": target})
        logger.info(f"ReconAgent {self.agent_id} created plan with {len(plan)} actions")
        return plan
    
    async def _llm_plan(self, target: Dict[str, Any], context: Dict[str, Any], persona_traits: Dict) -> List[Dict]:
        from core.agent_prompts import PLAN_USER_PROMPT
        prompt = PLAN_USER_PROMPT.format(
            target=json.dumps(target),
            context=json.dumps({k: str(v)[:200] for k, v in context.items()}),
            previous_actions=[a.get("action_type") for a in self.actions_taken[-5:]]
        )
        raw = await self.llm_client.generate_json(self._get_system_prompt(), prompt, max_tokens=2048)
        try:
            plan = json.loads(raw)
            if isinstance(plan, list) and len(plan) > 0:
                # Store LLM reasoning for this plan
                from datetime import datetime
                self.add_memory({
                    "type": "llm_reasoning",
                    "stage": "planning",
                    "reasoning": raw,
                    "timestamp": datetime.utcnow().isoformat()
                })
                return plan
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"ReconAgent {self.agent_id}: LLM plan parse failed, using fallback")
        return self._fallback_plan(target, persona_traits)
    
    def _fallback_plan(self, target: Dict[str, Any], persona_traits: Dict) -> List[Dict]:
        plan = []
        if persona_traits["stealth"] in ("high", "very_high"):
            plan.append({
                "action_type": "passive_recon",
                "description": "Perform passive reconnaissance using OSINT",
                "mitre_tactic": "TA0043", "mitre_technique": "T1593", "priority": 1
            })
        plan.append({
            "action_type": "port_scan",
            "description": f"Scan target {target.get('ip', 'unknown')} for open ports",
            "mitre_tactic": "TA0043", "mitre_technique": "T1046", "priority": 2
        })
        plan.append({
            "action_type": "service_enumeration",
            "description": "Enumerate services running on open ports",
            "mitre_tactic": "TA0043", "mitre_technique": "T1046", "priority": 3
        })
        plan.append({
            "action_type": "vulnerability_scan",
            "description": "Identify potential vulnerabilities",
            "mitre_tactic": "TA0043", "mitre_technique": "T1595", "priority": 4
        })
        if persona_traits["sophistication"] in ("high", "very_high"):
            plan.append({
                "action_type": "network_mapping",
                "description": "Map network topology and identify pivot points",
                "mitre_tactic": "TA0007", "mitre_technique": "T1590", "priority": 5
            })
        return plan
    
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status(AgentStatus.EXECUTING)
        action_type = action.get("action_type")
        
        if self.llm_client and self.llm_client.is_available:
            result, llm_reasoning = await self._llm_execute(action, context)
        else:
            result = await self._fallback_execute(action_type, context)
            llm_reasoning = None
        
        self.record_action({
            "action_type": action_type, "result": result,
            "mitre_tactic": action.get("mitre_tactic"),
            "mitre_technique": action.get("mitre_technique")
        }, llm_reasoning)
        self.update_status(AgentStatus.IDLE)
        return result
    
    async def _llm_execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
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
                if "findings" in result:
                    if "vulnerabilities" in result["findings"]:
                        self.vulnerabilities.extend(result["findings"]["vulnerabilities"])
                        result["vulnerabilities"] = result["findings"]["vulnerabilities"]
                    if "open_ports" in result["findings"]:
                        self.discovered_assets.extend(result["findings"]["open_ports"])
                        result["open_ports"] = result["findings"]["open_ports"]
                    if "services" in result["findings"]:
                        result["services"] = result["findings"]["services"]
                return result, raw
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"ReconAgent {self.agent_id}: LLM execute parse failed, using fallback")
        fallback_result = await self._fallback_execute(action.get("action_type"), context)
        return fallback_result, None
    
    async def _fallback_execute(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if action_type == "passive_recon":
            return await self._passive_recon(context)
        elif action_type == "port_scan":
            return await self._port_scan(context)
        elif action_type == "service_enumeration":
            return await self._service_enumeration(context)
        elif action_type == "vulnerability_scan":
            return await self._vulnerability_scan(context)
        elif action_type == "network_mapping":
            return await self._network_mapping(context)
        return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    async def _passive_recon(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        findings = {
            "dns_records": ["example.com", "mail.example.com", "www.example.com"],
            "whois_info": {"registrar": "Example Registrar", "creation_date": "2020-01-01"},
            "technologies": ["nginx", "php", "mysql"]
        }
        self.add_memory({"type": "discovery", "category": "passive_recon", "findings": findings})
        return {"success": True, "findings": findings, "description": "Passive reconnaissance completed — discovered DNS records and technology stack"}
    
    async def _port_scan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        persona_traits = self.get_persona_traits()
        if persona_traits["stealth"] == "low":
            open_ports = [22, 80, 443, 3306, 8080, 8443]
        else:
            open_ports = [22, 80, 443]
        port_info = [{"port": p, "state": "open", "service": self._guess_service(p)} for p in open_ports]
        self.discovered_assets.extend(port_info)
        self.add_memory({"type": "discovery", "category": "port_scan", "ports": port_info})
        return {"success": True, "open_ports": port_info, "description": f"Port scan complete — found {len(open_ports)} open ports"}
    
    async def _service_enumeration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        services = [
            {"port": 22, "service": "ssh", "version": "OpenSSH 8.2p1", "banner": "SSH-2.0-OpenSSH_8.2p1"},
            {"port": 80, "service": "http", "version": "nginx 1.18.0", "banner": "nginx/1.18.0"},
            {"port": 443, "service": "https", "version": "nginx 1.18.0", "ssl": True}
        ]
        self.add_memory({"type": "discovery", "category": "service_enumeration", "services": services})
        return {"success": True, "services": services, "description": f"Enumerated {len(services)} services with version info"}
    
    async def _vulnerability_scan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        vulnerabilities = [
            {"cve": "CVE-2024-1234", "severity": "high", "service": "nginx", "description": "Remote code execution in nginx worker process", "exploitable": True},
            {"cve": "CVE-2024-5678", "severity": "medium", "service": "ssh", "description": "Information disclosure via timing attack", "exploitable": False},
            {"cve": "CVE-2024-9012", "severity": "critical", "service": "http", "description": "SQL injection in web application login", "exploitable": True}
        ]
        self.vulnerabilities.extend(vulnerabilities)
        self.add_memory({"type": "discovery", "category": "vulnerabilities", "vulnerabilities": vulnerabilities})
        return {"success": True, "vulnerabilities": vulnerabilities, "description": f"Vulnerability scan found {len(vulnerabilities)} issues — {sum(1 for v in vulnerabilities if v['exploitable'])} exploitable"}
    
    async def _network_mapping(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        network_map = {
            "subnets": ["192.168.1.0/24"],
            "hosts": [
                {"ip": "192.168.1.1", "role": "gateway"},
                {"ip": "192.168.1.10", "role": "web_server"},
                {"ip": "192.168.1.20", "role": "database"},
                {"ip": "192.168.1.30", "role": "file_server"}
            ],
            "pivot_points": ["192.168.1.10"]
        }
        self.network_map = network_map
        self.add_memory({"type": "discovery", "category": "network_map", "network_map": network_map})
        return {"success": True, "network_map": network_map, "description": "Network mapped — identified 4 hosts and 1 pivot point"}
    
    async def adapt(self, feedback: Dict[str, Any]) -> None:
        if self.llm_client and self.llm_client.is_available and feedback.get("defense_injected"):
            defense = feedback.get("defense", {})
            prompt = ADAPT_USER_PROMPT.format(
                defense_type=defense.get("type", "unknown"),
                defense_details=json.dumps(defense),
                previous_actions=[a.get("action_type") for a in self.actions_taken[-5:]],
                context="Reconnaissance phase"
            )
            raw = await self.llm_client.generate_json(self._get_system_prompt(), prompt, max_tokens=1024)
            try:
                adaptation = json.loads(raw)
                self.add_memory({"type": "adaptation", "strategy": adaptation})
                logger.info(f"ReconAgent {self.agent_id} adapted: {adaptation.get('adaptation_strategy', 'unknown')}")
                return
            except (json.JSONDecodeError, TypeError):
                pass
        
        if feedback.get("blocked"):
            self.add_memory({"type": "adaptation", "reason": "scan_blocked", "action": "switch_to_stealth_mode"})
            logger.info(f"ReconAgent {self.agent_id} adapting to blocked scan")
        if feedback.get("detected"):
            self.add_memory({"type": "adaptation", "reason": "detection", "action": "pause_and_wait"})
            logger.info(f"ReconAgent {self.agent_id} detected, pausing operations")
    
    def _guess_service(self, port: int) -> str:
        common_ports = {22: "ssh", 80: "http", 443: "https", 3306: "mysql", 5432: "postgresql", 8080: "http-proxy", 8443: "https-alt"}
        return common_ports.get(port, "unknown")
