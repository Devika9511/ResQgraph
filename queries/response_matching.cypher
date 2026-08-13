MATCH (i:Incident {id:$incident_id})-[:OCCURS_AT]->(incident_location:Location)
MATCH (i)-[:REQUIRES_SPECIALTY]->(specialty:Specialty)
MATCH (p:Responder)-[:QUALIFIED_FOR]->(specialty)
MATCH (p)-[:BASED_AT]->(station:EmergencyStation)-[:LOCATED_AT]->(station_location:Location)
MATCH responder_path=(station_location)-[:CONNECTED_TO*0..7]-(incident_location)
MATCH (h:Hospital)-[:SPECIALIZES_IN]->(specialty)
MATCH (h)-[:LOCATED_AT]->(hospital_location:Location)
MATCH hospital_path=(incident_location)-[:CONNECTED_TO*1..7]-(hospital_location)
RETURN p.name AS responder,p.role AS responder_role,h.name AS hospital,specialty.name AS specialty,length(responder_path) AS responder_hops,length(hospital_path) AS hospital_hops
ORDER BY responder_hops+hospital_hops LIMIT 1;
