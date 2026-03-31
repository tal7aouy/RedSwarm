from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from api.routes.simulation import active_simulations
from core.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class DefenseInjection(BaseModel):
    type: str = Field(..., description="Defense type: firewall, edr, patch, block_port, rate_limit")
    config: Dict[str, Any] = Field(default={}, description="Defense configuration")


class InjectionResponse(BaseModel):
    simulation_id: str
    injection_id: str
    status: str
    message: str


@router.post("/{simulation_id}/inject", response_model=InjectionResponse)
async def inject_defense(simulation_id: str, defense: DefenseInjection):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    if orchestrator.status not in ["running", "initialized"]:
        raise HTTPException(status_code=400, detail="Cannot inject defense into non-running simulation")
    
    try:
        orchestrator.inject_defense({
            "type": defense.type,
            "config": defense.config
        })
        
        injection_id = f"injection_{len(orchestrator.god_mode.injections)}"
        
        logger.info(f"Injected {defense.type} defense into simulation {simulation_id}")
        
        return InjectionResponse(
            simulation_id=simulation_id,
            injection_id=injection_id,
            status="injected",
            message=f"Defense {defense.type} injected successfully"
        )
    
    except Exception as e:
        logger.error(f"Failed to inject defense: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{simulation_id}/defenses")
async def get_active_defenses(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "active_defenses": orchestrator.god_mode.get_active_defenses(),
        "injections": orchestrator.god_mode.injections
    }


@router.get("/defense-types")
async def get_defense_types():
    return {
        "defense_types": [
            {
                "type": "firewall",
                "description": "Block network traffic based on rules",
                "config_example": {
                    "rules": ["block_port_445", "block_smb"],
                    "default_policy": "deny"
                }
            },
            {
                "type": "edr",
                "description": "Endpoint Detection and Response system",
                "config_example": {
                    "detection_level": "high",
                    "monitored_processes": ["powershell.exe", "cmd.exe"]
                }
            },
            {
                "type": "patch",
                "description": "Apply security patches to vulnerabilities",
                "config_example": {
                    "cves": ["CVE-2024-1234", "CVE-2024-5678"]
                }
            },
            {
                "type": "block_port",
                "description": "Block specific network ports",
                "config_example": {
                    "ports": [445, 3389, 22]
                }
            },
            {
                "type": "rate_limit",
                "description": "Rate limit requests to prevent brute force",
                "config_example": {
                    "max_requests": 10,
                    "time_window": 60
                }
            }
        ]
    }
