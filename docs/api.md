# RedSwarm API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently, no authentication is required for local development. Production deployments should implement proper authentication.

## Endpoints

### Simulation Management

#### Start Simulation
```http
POST /simulation/start
```

**Request Body:**
```json
{
  "target": "192.168.1.100",
  "scenario": "ctf_bank_heist",
  "agent_types": ["recon", "exploit", "post_exploit"],
  "personas": {
    "recon": "apt29",
    "exploit": "apt29",
    "post_exploit": "apt29"
  }
}
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "status": "started",
  "message": "Simulation started successfully"
}
```

#### Get Simulation Status
```http
GET /simulation/{simulation_id}/status
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "status": "running",
  "agents": {
    "recon_abc123": {
      "type": "recon",
      "status": "executing",
      "actions_count": 5
    }
  }
}
```

#### Get Simulation Report
```http
GET /simulation/{simulation_id}/report
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "target": "192.168.1.100",
  "status": "completed",
  "duration_seconds": 120,
  "summary": {
    "vulnerabilities_found": 3,
    "access_gained": 2,
    "total_actions": 15,
    "successful_actions": 12
  },
  "attack_graph": {...},
  "mitre_attack_mapping": {...}
}
```

#### Stop Simulation
```http
POST /simulation/{simulation_id}/stop
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "status": "stopped"
}
```

#### List Simulations
```http
GET /simulation/list
```

**Response:**
```json
{
  "simulations": [
    {
      "id": 1,
      "target": "192.168.1.100",
      "scenario": "ctf_bank_heist",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### Agent Information

#### Get Agent Types
```http
GET /agents/types
```

**Response:**
```json
[
  {
    "agent_type": "recon",
    "description": "Reconnaissance agent for discovering targets",
    "capabilities": [
      "passive_recon",
      "port_scanning",
      "service_enumeration"
    ]
  }
]
```

#### Get Personas
```http
GET /agents/personas
```

**Response:**
```json
{
  "personas": {
    "apt28": {
      "name": "apt28",
      "description": "Sophisticated state-sponsored threat actor"
    }
  }
}
```

### God Mode

#### Inject Defense
```http
POST /god-mode/{simulation_id}/inject
```

**Request Body:**
```json
{
  "type": "firewall",
  "config": {
    "rules": ["block_port_445"],
    "default_policy": "deny"
  }
}
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "injection_id": "injection_1",
  "status": "injected",
  "message": "Defense firewall injected successfully"
}
```

#### Get Active Defenses
```http
GET /god-mode/{simulation_id}/defenses
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "active_defenses": {
    "firewall": {
      "enabled": true,
      "rules": ["block_port_445"]
    }
  },
  "injections": [...]
}
```

#### Get Defense Types
```http
GET /god-mode/defense-types
```

**Response:**
```json
{
  "defense_types": [
    {
      "type": "firewall",
      "description": "Block network traffic based on rules",
      "config_example": {...}
    }
  ]
}
```

### Reports

#### Get Report
```http
GET /reports/{simulation_id}?format=json
```

**Query Parameters:**
- `format`: `json` or `mitre_attack`

**Response:** See simulation report format above

#### Get Attack Chain
```http
GET /reports/{simulation_id}/attack-chain
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "attack_chain": [
    {
      "id": "action_0",
      "agent_id": "recon_abc123",
      "action_type": "port_scan",
      "result": {...},
      "success": true,
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

#### Get Attack Graph
```http
GET /reports/{simulation_id}/graph
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

#### Get MITRE Mapping
```http
GET /reports/{simulation_id}/mitre
```

**Response:**
```json
{
  "simulation_id": "abc123...",
  "mitre_attack": {
    "tactics": [
      {
        "tactic_id": "TA0043",
        "techniques": [...]
      }
    ],
    "technique_frequency": {
      "T1046": 3,
      "T1190": 2
    }
  }
}
```

### Scenarios

#### List Scenarios
```http
GET /scenarios/list
```

**Response:**
```json
[
  {
    "id": "ctf_bank_heist",
    "name": "Hack the Bank",
    "description": "Infiltrate a simulated banking system",
    "difficulty": "medium",
    "objectives": [...],
    "recommended_agents": ["recon", "exploit", "post_exploit"],
    "target_config": {...}
  }
]
```

#### Get Scenario
```http
GET /scenarios/{scenario_id}
```

**Response:** Single scenario object

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Currently no rate limiting in development. Production should implement:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## WebSocket (Future)

Real-time updates will be available via WebSocket:

```javascript
ws://localhost:8000/ws/simulation/{simulation_id}
```

**Message Format:**
```json
{
  "type": "action_completed",
  "data": {...}
}
```

---

For more details, visit the interactive API documentation at `http://localhost:8000/docs`
