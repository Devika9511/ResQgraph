def get_response_graph(driver, incident_id):

    query = """
    MATCH (i:Incident {id:$incident_id})
          -[:OCCURS_AT]->(start:Location)

    MATCH (i)-[:REQUIRES_SPECIALTY]->(specialty:Specialty)

    MATCH (h:Hospital)
          -[:SPECIALIZES_IN]->(specialty)

    MATCH (h)-[:LOCATED_AT]->(destination:Location)

    MATCH hospital_path =
          (start)-[:CONNECTED_TO*0..7]-(destination)

    WITH i,
         start,
         h,
         destination,
         hospital_path

    ORDER BY length(hospital_path) ASC

    LIMIT 1

    RETURN
        i,
        start,
        h,
        destination,
        hospital_path
    """

    with driver.session() as session:

        record = session.run(
            query,
            incident_id=incident_id
        ).single()

    if not record:
        return []

    incident = record["i"]
    start = record["start"]
    hospital = record["h"]
    destination = record["destination"]
    path = record["hospital_path"]

    # ---------------------------------------------------------
    # Graphviz
    # ---------------------------------------------------------

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'graph [bgcolor="transparent"];',
        'node [shape=box, style="rounded,filled", fontname="Arial"];'
    ]

    def safe(value):

        if value is None:
            return ""

        return (
            str(value)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

    def add_node(node_id, label):

        if node_id is None:
            return

        lines.append(
            f'"{safe(node_id)}" '
            f'[label="{safe(label)}"];'
        )

    def add_edge(source, target, label):

        if source is None or target is None:
            return

        lines.append(
            f'"{safe(source)}" -> "{safe(target)}" '
            f'[label="{safe(label)}"];'
        )

    # ---------------------------------------------------------
    # Incident
    # ---------------------------------------------------------

    add_node(
        incident["id"],
        f"🚨 Incident\\n{incident.get('type', '')}"
    )

    # ---------------------------------------------------------
    # Incident location
    # ---------------------------------------------------------

    add_node(
        start["id"],
        f"📍 Location\\n{start.get('name', '')}"
    )

    add_edge(
        incident["id"],
        start["id"],
        "OCCURS_AT"
    )

    # ---------------------------------------------------------
    # Connected locations
    # ---------------------------------------------------------

    if path is not None:

        for node in path.nodes:

            add_node(
                node["id"],
                f"📍 Location\\n{node.get('name', '')}"
            )

        for relationship in path.relationships:

            add_edge(
                relationship.start_node["id"],
                relationship.end_node["id"],
                "CONNECTED_TO"
            )

    # ---------------------------------------------------------
    # Hospital
    # ---------------------------------------------------------

    add_node(
        hospital["id"],
        f"🏥 Hospital\\n{hospital.get('name', '')}"
    )

    add_edge(
        destination["id"],
        hospital["id"],
        "LOCATED_AT"
    )

    # ---------------------------------------------------------
    # Finish Graphviz
    # ---------------------------------------------------------

    lines.append("}")

    return [
        {
            "dot": "\n".join(lines)
        }
    ]