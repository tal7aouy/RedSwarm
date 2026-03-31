from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.database import get_db, Simulation
from api.routes.simulation import active_simulations
from core.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.get("/{simulation_id}")
async def get_report(simulation_id: str, format: str = "json"):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    if format == "json":
        return orchestrator.generate_report(format="json")
    elif format == "mitre_attack":
        return _generate_mitre_report(orchestrator)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'mitre_attack'")


@router.get("/{simulation_id}/attack-chain")
async def get_attack_chain(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "attack_chain": orchestrator.attack_graph.get_attack_chain()
    }


@router.get("/{simulation_id}/graph")
async def get_attack_graph(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "graph": orchestrator.attack_graph.get_graph_visualization_data()
    }


@router.get("/{simulation_id}/mitre")
async def get_mitre_mapping(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    
    return {
        "simulation_id": simulation_id,
        "mitre_attack": orchestrator.attack_graph.get_mitre_mapping()
    }


def _generate_mitre_report(orchestrator):
    mitre_mapping = orchestrator.attack_graph.get_mitre_mapping()
    
    return {
        "simulation_id": orchestrator.simulation_id,
        "target": orchestrator.target,
        "mitre_attack_coverage": mitre_mapping,
        "summary": {
            "tactics_used": len(mitre_mapping.get("tactics", [])),
            "techniques_used": mitre_mapping.get("total_techniques", 0),
            "most_common_technique": max(
                mitre_mapping.get("technique_frequency", {}).items(),
                key=lambda x: x[1],
                default=("None", 0)
            )[0]
        }
    }
