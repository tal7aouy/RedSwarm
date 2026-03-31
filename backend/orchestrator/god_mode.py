from typing import Dict, List, Any
from datetime import datetime
from core.logger import setup_logger

logger = setup_logger(__name__)


class GodModeManager:
    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.injections: List[Dict[str, Any]] = []
        self.active_defenses: Dict[str, Any] = {}
        
    def inject_defense(self, defense: Dict[str, Any]):
        injection = {
            "id": f"injection_{len(self.injections)}",
            "type": defense.get("type"),
            "config": defense.get("config", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.injections.append(injection)
        
        defense_type = defense.get("type")
        if defense_type == "firewall":
            self._inject_firewall(defense.get("config", {}))
        elif defense_type == "edr":
            self._inject_edr(defense.get("config", {}))
        elif defense_type == "patch":
            self._inject_patch(defense.get("config", {}))
        elif defense_type == "block_port":
            self._inject_port_block(defense.get("config", {}))
        elif defense_type == "rate_limit":
            self._inject_rate_limit(defense.get("config", {}))
        
        logger.info(f"Injected defense: {defense_type}")
    
    def _inject_firewall(self, config: Dict[str, Any]):
        self.active_defenses["firewall"] = {
            "enabled": True,
            "rules": config.get("rules", []),
            "default_policy": config.get("default_policy", "allow")
        }
    
    def _inject_edr(self, config: Dict[str, Any]):
        self.active_defenses["edr"] = {
            "enabled": True,
            "detection_level": config.get("detection_level", "medium"),
            "monitored_processes": config.get("monitored_processes", [])
        }
    
    def _inject_patch(self, config: Dict[str, Any]):
        patched_cves = config.get("cves", [])
        if "patches" not in self.active_defenses:
            self.active_defenses["patches"] = []
        self.active_defenses["patches"].extend(patched_cves)
    
    def _inject_port_block(self, config: Dict[str, Any]):
        blocked_ports = config.get("ports", [])
        if "blocked_ports" not in self.active_defenses:
            self.active_defenses["blocked_ports"] = []
        self.active_defenses["blocked_ports"].extend(blocked_ports)
    
    def _inject_rate_limit(self, config: Dict[str, Any]):
        self.active_defenses["rate_limit"] = {
            "enabled": True,
            "max_requests": config.get("max_requests", 100),
            "time_window": config.get("time_window", 60)
        }
    
    def is_blocked(self, action: Dict[str, Any]) -> bool:
        action_type = action.get("action_type")
        
        if "firewall" in self.active_defenses and self.active_defenses["firewall"]["enabled"]:
            if action_type in ["port_scan", "exploit_vulnerability"]:
                logger.debug(f"Action {action_type} blocked by firewall")
                return True
        
        if "edr" in self.active_defenses and self.active_defenses["edr"]["enabled"]:
            if action_type in ["deploy_custom_payload", "establish_persistence"]:
                detection_level = self.active_defenses["edr"]["detection_level"]
                if detection_level in ["high", "very_high"]:
                    logger.debug(f"Action {action_type} blocked by EDR")
                    return True
        
        if "patches" in self.active_defenses:
            target_cve = action.get("target_cve")
            if target_cve and target_cve in self.active_defenses["patches"]:
                logger.debug(f"Action targeting {target_cve} blocked by patch")
                return True
        
        if "blocked_ports" in self.active_defenses:
            if action_type == "port_scan":
                logger.debug(f"Port scan blocked")
                return True
        
        if "rate_limit" in self.active_defenses and self.active_defenses["rate_limit"]["enabled"]:
            if action_type in ["brute_force", "port_scan"]:
                logger.debug(f"Action {action_type} rate limited")
                return True
        
        return False
    
    def get_active_defenses(self) -> Dict[str, Any]:
        return self.active_defenses
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "injections": self.injections,
            "active_defenses": self.active_defenses,
            "total_injections": len(self.injections)
        }
