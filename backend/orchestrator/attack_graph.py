from typing import Dict, List, Any, Optional
from datetime import datetime
import networkx as nx
from core.logger import setup_logger

logger = setup_logger(__name__)


class AttackGraph:
    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.graph = nx.DiGraph()
        self.actions: List[Dict[str, Any]] = []
        self.mitre_techniques: Dict[str, int] = {}
        
    def add_agent(self, agent_id: str, agent_type: str):
        self.graph.add_node(
            agent_id,
            type="agent",
            agent_type=agent_type,
            created_at=datetime.utcnow().isoformat()
        )
        logger.debug(f"Added agent {agent_id} to attack graph")
    
    def add_action(
        self,
        agent_id: str,
        action_type: str,
        result: Dict[str, Any],
        mitre_tactic: Optional[str] = None,
        mitre_technique: Optional[str] = None
    ):
        action_id = f"action_{len(self.actions)}"
        
        action = {
            "id": action_id,
            "agent_id": agent_id,
            "action_type": action_type,
            "result": result,
            "mitre_tactic": mitre_tactic,
            "mitre_technique": mitre_technique,
            "success": result.get("success", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.actions.append(action)
        
        self.graph.add_node(
            action_id,
            type="action",
            action_type=action_type,
            success=result.get("success", False),
            mitre_tactic=mitre_tactic,
            mitre_technique=mitre_technique,
            timestamp=action["timestamp"]
        )
        
        self.graph.add_edge(agent_id, action_id)
        
        if len(self.actions) > 1:
            prev_action_id = self.actions[-2]["id"]
            if self.actions[-2]["agent_id"] == agent_id:
                self.graph.add_edge(prev_action_id, action_id, relation="sequence")
        
        if mitre_technique:
            self.mitre_techniques[mitre_technique] = self.mitre_techniques.get(mitre_technique, 0) + 1
        
        logger.debug(f"Added action {action_id} to attack graph")
    
    def get_attack_chain(self) -> List[Dict[str, Any]]:
        return self.actions
    
    def get_mitre_mapping(self) -> Dict[str, Any]:
        tactics = {}
        
        for action in self.actions:
            tactic = action.get("mitre_tactic")
            technique = action.get("mitre_technique")
            
            if tactic and technique:
                if tactic not in tactics:
                    tactics[tactic] = {
                        "tactic_id": tactic,
                        "techniques": []
                    }
                
                tactics[tactic]["techniques"].append({
                    "technique_id": technique,
                    "action_type": action["action_type"],
                    "success": action["success"],
                    "timestamp": action["timestamp"]
                })
        
        return {
            "tactics": list(tactics.values()),
            "technique_frequency": self.mitre_techniques,
            "total_techniques": len(self.mitre_techniques)
        }
    
    def get_graph_visualization_data(self) -> Dict[str, Any]:
        nodes = []
        edges = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "type": node_data.get("type"),
                "label": node_data.get("action_type", node_data.get("agent_type", node_id)),
                "data": node_data
            })
        
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "relation": edge_data.get("relation", "default")
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "actions": self.actions,
            "graph_data": self.get_graph_visualization_data(),
            "statistics": {
                "total_actions": len(self.actions),
                "successful_actions": sum(1 for a in self.actions if a["success"]),
                "failed_actions": sum(1 for a in self.actions if not a["success"]),
                "unique_techniques": len(self.mitre_techniques)
            }
        }
