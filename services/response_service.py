def find_best_response(driver, incident_id):

    # =========================================================
    # HOSPITAL QUERY
    # =========================================================

    hospital_query = """
    MATCH (i:Incident {id:$incident_id})
          -[:OCCURS_AT]->(start:Location)

    MATCH (i)-[:REQUIRES_SPECIALTY]->(required:Specialty)

    MATCH (h:Hospital)
          -[:SPECIALIZES_IN]->(required)

    MATCH (h)-[:LOCATED_AT]->(destination:Location)

    MATCH path=(start)-[:CONNECTED_TO*0..7]-(destination)

    WITH h,
         required,
         path,
         reduce(
             d=0.0,
             r IN relationships(path) |
             d + coalesce(r.distance_km, 0.0)
         ) AS distance,
         reduce(
             t=0.0,
             r IN relationships(path) |
             t + coalesce(r.travel_time_min, 0.0)
         ) AS travel

    RETURN
        h.name AS name,
        required.name AS specialty,
        h.available_beds AS available_beds,
        distance AS distance_km,
        travel AS travel_time_min,
        length(path) AS hops

    ORDER BY travel ASC, available_beds DESC

    LIMIT 1
    """

    # =========================================================
    # AMBULANCE QUERY
    # =========================================================

    ambulance_query = """
    MATCH (i:Incident {id:$incident_id})
          -[:OCCURS_AT]->(incident_location:Location)

    MATCH (a:Ambulance)
          -[:LOCATED_AT]->(ambulance_location:Location)

    WHERE a.status = 'Available'

    MATCH path=(ambulance_location)
          -[:CONNECTED_TO*1..7]-
          (incident_location)

    WITH a,
         path,
         reduce(
             d=0.0,
             r IN relationships(path) |
             d + coalesce(r.distance_km, 0.0)
         ) AS distance,
         reduce(
             t=0.0,
             r IN relationships(path) |
             t + coalesce(r.travel_time_min, 0.0)
         ) AS travel

    RETURN
        a.name AS name,
        a.vehicle_type AS vehicle_type,
        distance AS distance_km,
        travel AS travel_time_min,
        length(path) AS hops

    ORDER BY travel ASC, distance ASC

    LIMIT 1
    """

    # =========================================================
    # RESPONDER QUERY
    # =========================================================

    responder_query = """
    MATCH (i:Incident {id:$incident_id})
          -[:OCCURS_AT]->(incident_location:Location)

    MATCH (i)-[:REQUIRES_SPECIALTY]->(specialty:Specialty)

    MATCH (p:Responder)
          -[:QUALIFIED_FOR]->(specialty)

    MATCH (p)-[:BASED_AT]->(station:EmergencyStation)

    MATCH (station)-[:LOCATED_AT]->(station_location:Location)

    MATCH path=(station_location)
          -[:CONNECTED_TO*1..7]-
          (incident_location)

    RETURN
        p.name AS name,
        p.role AS role,
        specialty.name AS specialty,
        length(path) AS hops

    ORDER BY hops ASC

    LIMIT 1
    """

    # =========================================================
    # RUN QUERIES
    # =========================================================

    with driver.session() as session:

        hospital_record = session.run(
            hospital_query,
            incident_id=incident_id
        ).single()

        ambulance_record = session.run(
            ambulance_query,
            incident_id=incident_id
        ).single()

        responder_record = session.run(
            responder_query,
            incident_id=incident_id
        ).single()

    # =========================================================
    # RETURN RESULTS
    # =========================================================

    return {
        "hospital": (
            hospital_record.data()
            if hospital_record
            else None
        ),

        "ambulance": (
            ambulance_record.data()
            if ambulance_record
            else None
        ),

        "responder": (
            responder_record.data()
            if responder_record
            else None
        ),
    }