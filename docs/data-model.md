# ResQGraph Data Model

ResQGraph uses a graph data model to represent emergency incidents, locations, hospitals, ambulances, emergency stations, responders, specialties and roads.

## Node Labels

### Incident
Properties:
- `id`
- `type`
- `severity`
- `description`
- `status`
- `created_at`

### Location
Properties:
- `id`
- `name`
- `latitude`
- `longitude`

### Road
Properties:
- `id`
- `name`

### Hospital
Properties:
- `id`
- `name`
- `capacity`
- `available_beds`

### Specialty
Properties:
- `name`

### Ambulance
Properties:
- `id`
- `name`
- `status`
- `vehicle_type`

### EmergencyStation
Properties:
- `id`
- `name`

### Responder
Properties:
- `id`
- `name`
- `role`

## Relationship Types

| Relationship | From | To | Properties |
|---|---|---|---|
| `OCCURS_AT` | Incident | Location | — |
| `REQUIRES_SPECIALTY` | Incident | Specialty | — |
| `CONNECTED_TO` | Location | Location | `distance_km`, `travel_time_min` |
| `USES_ROAD` | Location | Road | — |
| `LOCATED_AT` | Hospital | Location | — |
| `LOCATED_AT` | Ambulance | Location | — |
| `LOCATED_AT` | EmergencyStation | Location | — |
| `SPECIALIZES_IN` | Hospital | Specialty | — |
| `DISPATCHED_FROM` | Ambulance | EmergencyStation | — |
| `BASED_AT` | Responder | EmergencyStation | — |
| `QUALIFIED_FOR` | Responder | Specialty | — |

## Graph Data Model

```text
Incident
   │
   ├── OCCURS_AT ───────────────> Location
   │                                  │
   │                                  │ CONNECTED_TO
   │                                  │
   │                                  ▼
   │                              Location
   │                                  │
   │                                  │ CONNECTED_TO
   │                                  ▼
   │                              Location
   │                                  │
   │                              LOCATED_AT
   │                                  │
   │                                  ▼
   │                              Hospital
   │                                  │
   │                          SPECIALIZES_IN
   │                                  │
   │                                  ▼
   │                              Specialty
   │
   └── REQUIRES_SPECIALTY ───────────> Specialty

Responder
   │
   ├── QUALIFIED_FOR ────────────────> Specialty
   │
   └── BASED_AT ────────────────> EmergencyStation
                                      │
                                  LOCATED_AT
                                      │
                                      ▼
                                   Location

Ambulance
   │
   ├── DISPATCHED_FROM ────────> EmergencyStation
   │
   └── LOCATED_AT ─────────────> Location

Location ── CONNECTED_TO ── Location
                    │
                    ├── distance_km
                    └── travel_time_min
