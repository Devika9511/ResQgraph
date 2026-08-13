
## `docs/architecture.md`

Paste **only this**:

```markdown
# ResQGraph Architecture

ResQGraph uses a layered architecture that separates the Streamlit interface,
application services and CognoDB graph database.

## Architecture

```text
┌──────────────────────────────┐
│       Streamlit UI           │
│                              │
│ Dashboard                    │
│ Create Incident              │
│ Response Planner             │
│ Network Explorer             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Service Layer          │
│                              │
│ incident_service.py          │
│ response_service.py          │
│ route_service.py             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Official Neo4j Python      │
│          Driver              │
└──────────────┬───────────────┘
               │
          Bolt / openCypher
               │
               ▼
┌──────────────────────────────┐
│        CognoDB Cloud         │
│                              │
│     Graph Database           │
└──────────────────────────────┘
