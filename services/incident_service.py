from datetime import datetime


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats(driver):

    queries = {
        "incidents": """
            MATCH (n:Incident)
            RETURN count(n) AS value
        """,

        "hospitals": """
            MATCH (n:Hospital)
            RETURN count(n) AS value
        """,

        "ambulances": """
            MATCH (n:Ambulance)
            RETURN count(n) AS value
        """,

        "responders": """
            MATCH (n:Responder)
            RETURN count(n) AS value
        """,

        "locations": """
            MATCH (n:Location)
            RETURN count(n) AS value
        """
    }

    with driver.session() as session:

        return {
            key: session.run(query).single()["value"]
            for key, query in queries.items()
        }


# ============================================================
# GET LOCATIONS
# ============================================================

def get_locations(driver):

    query = """
        MATCH (l:Location)

        RETURN
            l.id AS id,
            l.name AS name

        ORDER BY l.name
    """

    with driver.session() as session:

        return [
            record.data()
            for record in session.run(query)
        ]


# ============================================================
# CREATE INCIDENT
# ============================================================

def create_incident(
    driver,
    incident_type,
    severity,
    location,
    specialty,
    description
):

    incident_id = (
        "INC-"
        + datetime.now().strftime("%y%m%d%H%M%S%f")[-12:]
    )

    query = """
        MATCH (l:Location {name:$location})

        MATCH (s:Specialty {name:$specialty})

        CREATE (
            i:Incident {
                id:$incident_id,
                type:$incident_type,
                severity:$severity,
                description:$description,
                status:'Active',
                created_at:datetime()
            }
        )

        CREATE
            (i)-[:OCCURS_AT]->(l)

        CREATE
            (i)-[:REQUIRES_SPECIALTY]->(s)

        RETURN i.id AS id
    """

    with driver.session() as session:

        record = session.run(
            query,
            location=location,
            specialty=specialty,
            incident_id=incident_id,
            incident_type=incident_type,
            severity=severity,
            description=description or ""
        ).single()

        return {
            "id": record["id"]
        }


# ============================================================
# GET RECENT INCIDENTS
# ============================================================

def get_recent_incidents(driver, limit=20):

    query = """
        MATCH
            (i:Incident)-[:OCCURS_AT]->(l:Location)

        OPTIONAL MATCH
            (i)-[:REQUIRES_SPECIALTY]->(s:Specialty)

        RETURN
            i.id AS id,
            i.type AS type,
            i.severity AS severity,
            i.status AS status,
            l.name AS location,
            s.name AS specialty,
            i.created_at AS created_at

        ORDER BY i.created_at DESC

        LIMIT $limit
    """

    with driver.session() as session:

        records = session.run(
            query,
            limit=limit
        )

        incidents = []

        for record in records:

            data = record.data()

            # ------------------------------------------------
            # IMPORTANT:
            # Neo4j returns created_at as neo4j.time.DateTime.
            # Streamlit/PyArrow cannot directly display it.
            # Convert it to a normal string.
            # ------------------------------------------------

            if data.get("created_at") is not None:

                data["created_at"] = str(
                    data["created_at"]
                )

            incidents.append(data)

        return incidents


# ============================================================
# GET SINGLE INCIDENT
# ============================================================

def get_incident(driver, incident_id):

    query = """
        MATCH
            (i:Incident {id:$incident_id})
            -[:OCCURS_AT]->(l:Location)

        OPTIONAL MATCH
            (i)-[:REQUIRES_SPECIALTY]->(s:Specialty)

        RETURN
            i.id AS id,
            i.type AS type,
            i.severity AS severity,
            i.status AS status,
            i.description AS description,
            l.name AS location,
            s.name AS specialty,
            i.created_at AS created_at
    """

    with driver.session() as session:

        record = session.run(
            query,
            incident_id=incident_id
        ).single()

        if not record:

            return None

        data = record.data()

        # ----------------------------------------------------
        # Convert Neo4j DateTime to string
        # ----------------------------------------------------

        if data.get("created_at") is not None:

            data["created_at"] = str(
                data["created_at"]
            )

        return data