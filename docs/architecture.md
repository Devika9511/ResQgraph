# ResQGraph Architecture

```text
Streamlit UI
    |
Service layer
    |
Official Neo4j Python Driver
    |
Bolt / openCypher
    |
CognoDB Cloud
```

The service layer separates UI concerns from database access and graph queries.
