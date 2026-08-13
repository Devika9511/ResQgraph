MATCH path=(start:Location {id:$start_id})-[:CONNECTED_TO*1..7]-(destination:Location {id:$destination_id})
WITH path,reduce(d=0.0,r IN relationships(path)|d+r.distance_km) AS distance,reduce(t=0.0,r IN relationships(path)|t+r.travel_time_min) AS travel
RETURN path,distance,travel,length(path) AS hops ORDER BY travel LIMIT 1;
