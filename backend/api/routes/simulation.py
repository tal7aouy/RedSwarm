from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.database import get_db, Simulation
from orchestrator import SwarmOrchestrator
from core.logger import setup_logger
import asyncio

router = APIRouter()
logger = setup_logger(__name__)

active_simulations: Dict[str, SwarmOrchestrator] = {}


class SimulationRequest(BaseModel):
    target: str = Field(..., description="Target IP or domain")
    scenario: Optional[str] = Field(None, description="Scenario name")
    agent_types: List[str] = Field(default=["recon", "exploit", "post_exploit"], description="Agent types to deploy")
    personas: Optional[Dict[str, str]] = Field(default={}, description="Agent personas")


class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    message: str


@router.post("/start", response_model=SimulationResponse)
async def start_simulation(request: SimulationRequest, db: Session = Depends(get_db)):
    try:
        if not _validate_target(request.target):
            raise HTTPException(status_code=400, detail="Invalid target. Only lab/local IPs allowed.")
        
        orchestrator = SwarmOrchestrator(
            target=request.target,
            scenario=request.scenario,
            agent_types=request.agent_types,
            personas=request.personas
        )
        
        simulation = Simulation(
            target=request.target,
            scenario=request.scenario,
            status="running",
            config={
                "agent_types": request.agent_types,
                "personas": request.personas
            }
        )
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        
        active_simulations[orchestrator.simulation_id] = orchestrator
        
        asyncio.create_task(_run_simulation(orchestrator, db, simulation.id))
        
        logger.info(f"Started simulation {orchestrator.simulation_id}")
        
        return SimulationResponse(
            simulation_id=orchestrator.simulation_id,
            status="started",
            message="Simulation started successfully"
        )
    
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    return orchestrator.get_status()


@router.get("/{simulation_id}/report")
async def get_simulation_report(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    return orchestrator.generate_report()


@router.post("/{simulation_id}/stop")
async def stop_simulation(simulation_id: str):
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    orchestrator = active_simulations[simulation_id]
    orchestrator.status = "stopped"
    
    logger.info(f"Stopped simulation {simulation_id}")
    
    return {"simulation_id": simulation_id, "status": "stopped"}


@router.get("/list")
async def list_simulations(db: Session = Depends(get_db)):
    simulations = db.query(Simulation).order_by(Simulation.created_at.desc()).limit(50).all()
    
    return {
        "simulations": [
            {
                "id": sim.id,
                "target": sim.target,
                "scenario": sim.scenario,
                "status": sim.status,
                "created_at": sim.created_at.isoformat()
            }
            for sim in simulations
        ]
    }


async def _run_simulation(orchestrator: SwarmOrchestrator, db: Session, simulation_id: int):
    try:
        await orchestrator.execute()
        
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if simulation:
            simulation.status = "completed"
            simulation.result = orchestrator.generate_report()
            db.commit()
        
        logger.info(f"Simulation {orchestrator.simulation_id} completed")
    
    except Exception as e:
        logger.error(f"Simulation {orchestrator.simulation_id} failed: {e}", exc_info=True)
        
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if simulation:
            simulation.status = "failed"
            db.commit()


def _validate_target(target: str) -> bool:
    import ipaddress
    
    try:
        ip = ipaddress.ip_address(target)
        
        allowed_ranges = [
            ipaddress.ip_network("192.168.0.0/16"),
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("127.0.0.0/8")
        ]
        
        return any(ip in network for network in allowed_ranges)
    
    except ValueError:
        return target in ["localhost", "example.com", "test.local"]
