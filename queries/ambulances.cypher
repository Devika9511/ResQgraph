MATCH (i:Incident {id:$incident_id})-[:OCCURS_AT]->(incident_location:Location)
MATCH (a:Ambulance)-[:LOCATED_AT]->(ambulance_location:Location)
WHERE a.status='Available'
MATCH path=(ambulance_location)-[:CONNECTED_TO*0..7]-(incident_location)
WITH a,path,reduce(t=0.0,r IN relationships(path)|t+r.travel_time_min) AS travel
RETURN a.name AS ambulance,a.vehicle_type AS vehicle_type,length(path) AS hops,travel
ORDER BY travel LIMIT 5;
