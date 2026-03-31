# RedSwarm Architecture

## Overview

RedSwarm is a multi-agent AI red teaming simulator built on a microservices architecture with real-time communication and graph-based attack modeling.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (Vue 3 + Vite)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Home   │  │Simulation│  │ Scenarios│  │ Reports  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                      API Gateway                             │
│                    (FastAPI)                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Simulation│  │  Agents  │  │God Mode  │  │ Reports  │  │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Swarm Orchestrator                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Agent Management                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Recon   │  │ Exploit  │  │Post-Exp  │          │  │
│  │  │  Agent   │  │  Agent   │  │  Agent   │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Attack Graph                             │  │
│  │         (NetworkX + Neo4j)                           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              God Mode Manager                         │  │
│  │         (Defense Injection)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ SQLite   │  │  Neo4j   │  │  Redis   │  │  LLM API │  │
│  │(Metadata)│  │ (Graph)  │  │ (Cache)  │  │(OpenAI)  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (Vue 3)

**Technology Stack:**
- Vue 3 with Composition API
- Vite for build tooling
- TailwindCSS for styling
- Pinia for state management
- Axios for API communication

**Key Features:**
- Real-time simulation dashboard
- Interactive attack graph visualization
- God Mode defense injection interface
- CTF scenario browser

### 2. Backend API (FastAPI)

**Technology Stack:**
- FastAPI for REST API
- SQLAlchemy for ORM
- Pydantic for validation
- Uvicorn for ASGI server

**Endpoints:**
- `/api/v1/simulation/*` - Simulation management
- `/api/v1/agents/*` - Agent information
- `/api/v1/god-mode/*` - Defense injection
- `/api/v1/reports/*` - Report generation
- `/api/v1/scenarios/*` - Scenario management

### 3. Agent System

**Base Agent Architecture:**
```python
class BaseAgent(ABC):
    - agent_id: str
    - agent_type: str
    - persona: AgentPersona
    - memory: List[Dict]
    - actions_taken: List[Dict]
    
    @abstractmethod
    async def plan() -> List[Action]
    
    @abstractmethod
    async def execute(action) -> Result
    
    @abstractmethod
    async def adapt(feedback) -> None
```

**Agent Types:**

1. **ReconAgent**
   - Passive reconnaissance
   - Port scanning
   - Service enumeration
   - Vulnerability scanning
   - Network mapping

2. **ExploitAgent**
   - Vulnerability exploitation
   - Brute force attacks
   - Custom payload deployment
   - Credential attacks

3. **PostExploitAgent**
   - Privilege escalation
   - Persistence establishment
   - Lateral movement
   - Data collection
   - Data exfiltration
   - Track covering

4. **InsiderAgent**
   - Legitimate access abuse
   - Internal reconnaissance
   - Data theft
   - System sabotage

### 4. Swarm Orchestrator

**Responsibilities:**
- Agent lifecycle management
- Attack phase coordination
- Context sharing between agents
- God Mode integration
- Report generation

**Execution Flow:**
```
1. Initialize agents with personas
2. Run reconnaissance phase
3. Share discovered vulnerabilities
4. Run exploitation phase
5. Share gained access
6. Run post-exploitation phase
7. Generate comprehensive report
```

### 5. Attack Graph

**Technology:**
- NetworkX for in-memory graph
- Neo4j for persistent storage (optional)

**Structure:**
```
Nodes:
- Agent nodes (agent_id, type, persona)
- Action nodes (action_id, type, result, MITRE mapping)

Edges:
- Agent -> Action (execution)
- Action -> Action (sequence)
- Action -> Asset (discovery/compromise)
```

### 6. God Mode Manager

**Defense Types:**
- Firewall rules
- EDR deployment
- Vulnerability patches
- Port blocking
- Rate limiting

**Injection Process:**
1. User injects defense via API
2. God Mode updates active defenses
3. Agents check defenses before actions
4. Blocked actions trigger adaptation
5. Agents modify tactics

### 7. MITRE ATT&CK Integration

**Mapping:**
- Every action tagged with Tactic ID (TA####)
- Every action tagged with Technique ID (T####)
- Real-time coverage visualization
- Technique frequency analysis

**Example Mappings:**
```
Port Scan -> TA0043 (Reconnaissance) -> T1046 (Network Service Discovery)
Exploit -> TA0002 (Execution) -> T1190 (Exploit Public-Facing Application)
Privilege Escalation -> TA0004 (Privilege Escalation) -> T1068 (Exploitation for Privilege Escalation)
```

## Data Flow

### Simulation Start
```
User -> Frontend -> API -> Orchestrator
                              ├─> Initialize Agents
                              ├─> Create Attack Graph
                              ├─> Initialize God Mode
                              └─> Start Execution
```

### Agent Execution
```
Agent.plan() -> List[Actions]
    ↓
For each Action:
    ├─> Check God Mode (blocked?)
    ├─> Execute Action
    ├─> Record in Attack Graph
    ├─> Update Context
    └─> Adapt if needed
```

### God Mode Injection
```
User -> Frontend -> API -> God Mode Manager
                              ├─> Update Active Defenses
                              └─> Notify Agents
                                    ↓
                              Agents.adapt()
```

## Security Considerations

### Target Validation
- Only allows private IP ranges
- Validates against whitelist
- Prevents real-world targeting

### Simulation Isolation
- Each simulation runs independently
- No cross-simulation data leakage
- Proper cleanup on completion

### API Security
- CORS protection
- Rate limiting
- Input validation
- Error handling

## Scalability

### Horizontal Scaling
- Stateless API design
- Redis for session management
- Load balancer ready

### Performance Optimization
- Async/await throughout
- Connection pooling
- Caching strategies
- Lazy loading

## Monitoring & Logging

### Logging Levels
- DEBUG: Detailed agent actions
- INFO: Simulation lifecycle
- WARNING: Blocked actions, adaptations
- ERROR: Failures, exceptions

### Metrics
- Simulation duration
- Action success rate
- Agent performance
- API response times

## Future Enhancements

1. **Real-time Collaboration**
   - WebSocket for live updates
   - Multi-user simulations

2. **Advanced Visualizations**
   - 3D attack graphs
   - Timeline animations
   - Heat maps

3. **Machine Learning**
   - Agent behavior learning
   - Attack pattern recognition
   - Predictive defense suggestions

4. **Integration APIs**
   - SIEM integration
   - Ticketing systems
   - Reporting tools

---

For implementation details, see individual component documentation.
