from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from agents import AgentPersona
from core.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class AgentInfo(BaseModel):
    agent_type: str
    description: str
    capabilities: List[str]


@router.get("/types", response_model=List[AgentInfo])
async def get_agent_types():
    return [
        AgentInfo(
            agent_type="recon",
            description="Reconnaissance agent for discovering targets and vulnerabilities",
            capabilities=[
                "passive_recon",
                "port_scanning",
                "service_enumeration",
                "vulnerability_scanning",
                "network_mapping"
            ]
        ),
        AgentInfo(
            agent_type="exploit",
            description="Exploitation agent for gaining access to systems",
            capabilities=[
                "exploit_vulnerabilities",
                "brute_force_attacks",
                "custom_payload_deployment",
                "credential_attacks"
            ]
        ),
        AgentInfo(
            agent_type="post_exploit",
            description="Post-exploitation agent for maintaining access and achieving objectives",
            capabilities=[
                "privilege_escalation",
                "persistence",
                "lateral_movement",
                "data_collection",
                "data_exfiltration",
                "cover_tracks"
            ]
        ),
        AgentInfo(
            agent_type="insider",
            description="Insider threat agent simulating malicious insider behavior",
            capabilities=[
                "abuse_legitimate_access",
                "internal_reconnaissance",
                "data_theft",
                "sabotage"
            ]
        )
    ]


@router.get("/personas")
async def get_personas():
    personas = {}
    
    for persona in AgentPersona:
        if persona == AgentPersona.GENERIC:
            continue
        
        personas[persona.value] = {
            "name": persona.value,
            "description": _get_persona_description(persona)
        }
    
    return {"personas": personas}


def _get_persona_description(persona: AgentPersona) -> str:
    descriptions = {
        AgentPersona.APT28: "Sophisticated state-sponsored threat actor (Fancy Bear)",
        AgentPersona.APT29: "Advanced persistent threat group (Cozy Bear)",
        AgentPersona.LAZARUS: "North Korean threat group focused on financial gain",
        AgentPersona.SCRIPT_KIDDIE: "Low-skill attacker using automated tools",
        AgentPersona.INSIDER: "Malicious insider with legitimate access",
        AgentPersona.RANSOMWARE: "Ransomware operator focused on encryption and extortion"
    }
    return descriptions.get(persona, "Unknown persona")
