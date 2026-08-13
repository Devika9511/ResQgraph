MATCH (i:Incident {id:$incident_id})-[:OCCURS_AT]->(start:Location)
MATCH (i)-[:REQUIRES_SPECIALTY]->(specialty:Specialty)
MATCH (h:Hospital)-[:SPECIALIZES_IN]->(specialty)
MATCH (h)-[:LOCATED_AT]->(destination:Location)
MATCH path=(start)-[:CONNECTED_TO*1..7]-(destination)
WITH h,specialty,path,reduce(t=0.0,r IN relationships(path)|t+r.travel_time_min) AS travel
RETURN h.name AS hospital,specialty.name AS specialty,length(path) AS hops,travel
ORDER BY travel LIMIT 5;
