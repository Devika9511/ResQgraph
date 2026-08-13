def create_schema(driver):
    statements=[
    'CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (n:Incident) REQUIRE n.id IS UNIQUE',
    'CREATE CONSTRAINT location_id IF NOT EXISTS FOR (n:Location) REQUIRE n.id IS UNIQUE',
    'CREATE CONSTRAINT hospital_id IF NOT EXISTS FOR (n:Hospital) REQUIRE n.id IS UNIQUE',
    'CREATE CONSTRAINT ambulance_id IF NOT EXISTS FOR (n:Ambulance) REQUIRE n.id IS UNIQUE',
    'CREATE CONSTRAINT responder_id IF NOT EXISTS FOR (n:Responder) REQUIRE n.id IS UNIQUE',
    'CREATE CONSTRAINT station_id IF NOT EXISTS FOR (n:EmergencyStation) REQUIRE n.id IS UNIQUE']
    with driver.session() as session:
        for statement in statements: session.run(statement)
