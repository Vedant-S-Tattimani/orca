# ORCA Backend Implementation

This repository contains the implementation of the ORCA (Marine EcoSystem Reasoning with Collaborative Agents) backend as described in the system architecture document.

## Overview

ORCA is a multi-agent, RAG-augmented, geospatially-aware reasoning system designed to provide explainable, evidence-backed answers to marine-related questions from stakeholders such as fishermen, coastal authorities, and disaster-management agencies.

## Architecture

The backend follows a layered architecture:

1. **Interface Layer** (`app/interface/`) - Input parsing, NLU, language handling
2. **Orchestrator Layer** (`app/orchestrator/`) - Planning, location resolution, merging
3. **Specialist Agents** (`app/agents/`) - Domain experts (weather, sea-state, hazards, PFZ/satellite)
4. **Data & Retrieval Layer** (`app/data_layer/`) - Geospatial, raster, vector store, models
5. **Rules Layer** (`app/rules/`) - Deterministic risk thresholds and engine
6. **Synthesis Layer** (`app/synthesis/`) - Reasoning/LLM, evidence tracking
7. **Response Layer** (`app/response/`) - Card building, SMS/IVR formatting
8. **Ingestion Layer** (`app/ingestion/`) - Scheduled jobs for external data

## Key Features

- **Decomposed by data domain**: Each specialist agent handles a specific data domain
- **Geospatial-first**: Location-aware queries with radius-based searches
- **Evidence-based**: Every claim is traceable to (source, field, timestamp) triples
- **Deterministic rules**: Risk assessment uses predefined thresholds, not LLM computation
- **Graceful degradation**: Handles missing data sources and partial failures
- **Multi-format output**: JSON, HTML, text, SMS, and IVR formats

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for full setup with PostGIS)
- API keys for external services (INCOIS, IMD, ISRO Bhuvan, LLM provider)

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your API keys
4. For full setup with database: `docker-compose up -d`

### Running the Demo

To see the end-to-end fishing safety check example:

```bash
python demo_fishing_safety.py
```

This will simulate the query: "Is it safe for me to go fishing tomorrow morning near Kollam?"

## Testing

Run tests with pytest:

```bash
pytest
```

## Components Implemented

- ✅ Main FastAPI application (`app/main.py`)
- ✅ Configuration management (`app/config.py`)
- ✅ Interface layer (schemas, NLU stubs)
- ✅ Orchestrator layer (planner, location resolver, merger)
- ✅ Specialist agents (weather, sea-state, hazard, PFZ/satellite) with base agent
- ✅ Data layer stubs (geospatial, raster, vector store, models)
- ✅ Rules layer (thresholds.yaml, risk engine)
- ✅ Synthesis layer (evidence tracker, synthesis agent, LLM client)
- ✅ Response layer (card builder, SMS/IVR formatter)
- ✅ Docker configuration (Dockerfile, docker-compose.yml)
- ✅ Comprehensive test suite
- ✅ End-to-end demo script

## Future Work

- Implement actual API integrations with INCOIS, IMD, ISRO sources
- Set up PostGIS with actual marine buoys, PFZ polygons, hazard zones data
- Implement vector store with real advisory document ingestion
- Add caching layer (Redis) for improved performance
- Implement authentication and rate limiting
- Add comprehensive API documentation (Swagger/OpenAPI)
- Implement actual LLM provider integrations
- Add monitoring and logging enhancements
- Implement SMS/IVR gateway integrations

## License

This implementation is for educational/demo purposes based on the ORCA architecture document.