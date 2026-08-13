# 🚨 ResQGraph — Emergency Resource Discovery & Response Network

ResQGraph is a graph-backed web application that finds connected emergency resources for an incident: an available ambulance, a qualified responder and a suitable hospital. It uses CognoDB Cloud with the official Neo4j Python driver and openCypher over Bolt.

## 🌐 Live Demo

🚀 **Deployed Application:**  
https://resqgraph.streamlit.app/

💻 **GitHub Repository:**  
https://github.com/Devika9511/ResQgraph

## Why a graph database?

The important questions are about connections rather than isolated rows: how locations connect, how emergency stations connect responders, and how an incident connects to hospitals with the required specialty. Variable-length `CONNECTED_TO` traversals make these network queries natural. Relationship properties `distance_km` and `travel_time_min` allow route ranking.

```text
Incident -> Location -> connected Locations -> Hospital
Incident -> Location -> Emergency Station -> Responder -> Specialty
```

## Data model

Nodes: Incident, Location, Road, Hospital, Specialty, Ambulance, EmergencyStation, Responder.

Relationships: OCCURS_AT, REQUIRES_SPECIALTY, CONNECTED_TO, USES_ROAD, LOCATED_AT, SPECIALIZES_IN, DISPATCHED_FROM, BASED_AT, QUALIFIED_FOR.

See `docs/data-model.md` and `docs/architecture.md`.

## Requirements covered

- Thoughtful labeled graph model: yes
- Typed relationships and properties: yes
- Realistic seed script: yes
- Multi-hop traversal: `queries/hospitals.cypher`
- Relationally awkward relationship query: `queries/response_matching.cypher`
- Parameterized Neo4j driver queries: yes
- Functional web application: Streamlit
- Loading state: response planner spinner
- Empty states: dashboard, planner and explorer
- Database error handling: startup connection check
- Environment variables: `.env`, excluded by `.gitignore`
- Hosted demo: deploy to Streamlit Community Cloud
- Screen recording: record the end-to-end response workflow

## Setup

1. Create a CognoDB Cloud account at https://console.cognodb.com/signup.
2. Create a free c0 instance.
3. Copy the `bolt+s://...databases.cognodb.cloud` URI and generated password.
4. Create `.env` from `.env.example`.
5. Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

6. Seed CognoDB:

```bash
python database/seed.py
```

7. Run:

```bash
streamlit run app.py
```

## Environment

```text
COGNODB_URI=bolt+s://<instance-id>.databases.cognodb.cloud
COGNODB_USERNAME=cognodb
COGNODB_PASSWORD=<generated-password>
```

Never commit `.env`.

## Main query

```cypher
MATCH (i:Incident {id:$incident_id})-[:OCCURS_AT]->(start:Location)
MATCH (i)-[:REQUIRES_SPECIALTY]->(specialty:Specialty)
MATCH (h:Hospital)-[:SPECIALIZES_IN]->(specialty)
MATCH (h)-[:LOCATED_AT]->(destination:Location)
MATCH path=(start)-[:CONNECTED_TO*1..7]-(destination)
WITH h,specialty,path,
     reduce(t=0.0,r IN relationships(path)|t+r.travel_time_min) AS travel
RETURN h.name AS hospital,specialty.name AS specialty,length(path) AS hops,travel
ORDER BY travel LIMIT 5;
```

## Project structure

```text
resqgraph/
├── app.py
├── database/
│   ├── connection.py
│   ├── schema.py
│   └── seed.py
├── services/
│   ├── incident_service.py
│   ├── response_service.py
│   └── route_service.py
├── queries/
│   ├── incidents.cypher
│   ├── hospitals.cypher
│   ├── ambulances.cypher
│   ├── routes.cypher
│   └── response_matching.cypher
├── docs/
├── assets/screenshots/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Deployment

Deploy `app.py` to Streamlit Community Cloud and configure `COGNODB_URI`, `COGNODB_USERNAME`, and `COGNODB_PASSWORD` as deployment secrets. Keep the CognoDB instance running for reviewer access.

## Screenshots

After running the application, add screenshots of Dashboard, Create Incident, Response Planner and Network Explorer under `assets/screenshots/` and embed them here before submission.
