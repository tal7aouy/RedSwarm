# Contributing to RedSwarm

Thank you for your interest in contributing to RedSwarm! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow ethical security practices

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/tal7aouy/RedSwarm.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push and create a Pull Request

## Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev -- --port 3000

# Visit: http://localhost:3000
```

## Project Structure

```
RedSwarm/
├── backend/
│   ├── agents/          # AI agent implementations (Recon, Exploit, PostExploit, Insider)
│   ├── api/             # FastAPI routes (simulation, agents, reports, god-mode)
│   ├── core/            # Core configuration (LLM client, logger, database)
│   ├── orchestrator/    # Swarm orchestration (attack graph, agent coordination)
│   └── main.py          # FastAPI entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # Vue components (Navbar, Cards, etc.)
│   │   ├── views/       # Page views (Home, Simulation, Scenarios, Reports)
│   │   ├── composables 
│   │   ├── router
│   │   ├── stores/      # Pinia stores (simulation state)
│   │   └── services/    # API services (axios client)
│   └── package.json
├── docs/                # Documentation (API, architecture)
├── .env.example         # Environment variables template
├── setup.sh            # One-command setup script
└── README.md           # Project documentation
```

## Contribution Areas

### 1. New Agent Types
Add new agent types in `backend/agents/`:
- Inherit from `BaseAgent`
- Implement `plan()`, `execute()`, and `adapt()` methods
- Add MITRE ATT&CK mappings

### 2. New Scenarios
Add scenarios in `backend/api/routes/scenarios.py`:
- Define objectives
- Configure target environment
- Specify recommended agents

### 3. Frontend Features
- Improve visualizations
- Add new dashboard widgets
- Enhance user experience

### 4. MITRE ATT&CK Integration
- Expand technique coverage
- Improve mapping accuracy
- Add technique descriptions

### 5. Documentation
- Improve README
- Add tutorials
- Write API documentation

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings
- Run: `black . && flake8 .`

### JavaScript/Vue
- Use ES6+ features
- Follow Vue 3 Composition API style
- Run: `npm run lint && npm run format`

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Request review from maintainers

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## Security

**Do not** open public issues for security vulnerabilities. Use [GitHub Security Advisories](https://github.com/tal7aouy/RedSwarm/security/advisories/new) to report privately, or follow [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under AGPL-3.0.

## Questions?

- **Issues**: [GitHub Issues](https://github.com/tal7aouy/RedSwarm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tal7aouy/RedSwarm/discussions)
- **Twitter**: [@RedSwarmAI](https://twitter.com/RedSwarmAI)

---

Thank you for contributing to RedSwarm! 🔴
