from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from core.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class Scenario(BaseModel):
    id: str
    name: str
    description: str
    difficulty: str
    objectives: List[str]
    recommended_agents: List[str]
    target_config: Dict[str, Any]


@router.get("/list", response_model=List[Scenario])
async def list_scenarios():
    return [
        Scenario(
            id="ctf_bank_heist",
            name="Hack the Bank",
            description="Infiltrate a simulated banking system and exfiltrate customer data",
            difficulty="medium",
            objectives=[
                "Gain initial access to the web server",
                "Escalate privileges to root",
                "Access the customer database",
                "Exfiltrate sensitive data"
            ],
            recommended_agents=["recon", "exploit", "post_exploit"],
            target_config={
                "target": "192.168.1.100",
                "services": ["http", "ssh", "mysql"],
                "vulnerabilities": ["CVE-2024-1234"]
            }
        ),
        Scenario(
            id="bypass_zero_trust",
            name="Bypass Zero Trust",
            description="Circumvent a zero-trust architecture and move laterally",
            difficulty="hard",
            objectives=[
                "Bypass multi-factor authentication",
                "Gain access to internal network",
                "Move laterally between segments",
                "Maintain persistence"
            ],
            recommended_agents=["recon", "exploit", "post_exploit"],
            target_config={
                "target": "10.0.0.50",
                "services": ["https", "vpn"],
                "defenses": ["mfa", "network_segmentation", "edr"]
            }
        ),
        Scenario(
            id="insider_threat",
            name="Insider Threat",
            description="Simulate a malicious insider stealing intellectual property",
            difficulty="medium",
            objectives=[
                "Abuse legitimate access",
                "Access sensitive documents",
                "Exfiltrate data via legitimate channels",
                "Cover tracks"
            ],
            recommended_agents=["insider"],
            target_config={
                "target": "internal.company.local",
                "access_level": "employee",
                "sensitive_data": ["source_code", "financial_reports", "customer_data"]
            }
        ),
        Scenario(
            id="ransomware_attack",
            name="Ransomware Simulation",
            description="Simulate a ransomware attack from initial access to encryption",
            difficulty="hard",
            objectives=[
                "Gain initial access via phishing",
                "Disable security controls",
                "Spread across network",
                "Encrypt critical systems"
            ],
            recommended_agents=["recon", "exploit", "post_exploit"],
            target_config={
                "target": "192.168.10.0/24",
                "services": ["smb", "rdp", "http"],
                "critical_systems": ["file_server", "domain_controller", "backup_server"]
            }
        ),
        Scenario(
            id="apt_campaign",
            name="APT Campaign",
            description="Advanced persistent threat targeting a corporate network",
            difficulty="very_hard",
            objectives=[
                "Establish initial foothold",
                "Deploy custom malware",
                "Maintain long-term persistence",
                "Exfiltrate data over months"
            ],
            recommended_agents=["recon", "exploit", "post_exploit"],
            target_config={
                "target": "corporate.example.com",
                "duration": "long_term",
                "stealth_required": True,
                "personas": {
                    "recon": "apt29",
                    "exploit": "apt29",
                    "post_exploit": "apt29"
                }
            }
        )
    ]


@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    scenarios = await list_scenarios()
    
    for scenario in scenarios:
        if scenario.id == scenario_id:
            return scenario
    
    raise HTTPException(status_code=404, detail="Scenario not found")
