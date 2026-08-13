from database.connection import get_driver
from database.schema import create_schema

LOCATIONS=[('L001','Central Campus Gate',17.4485,78.3498),('L002','Engineering Block',17.4502,78.3510),('L003','Student Hostel',17.4520,78.3531),('L004','City Junction',17.4468,78.3470),('L005','Main Market',17.4445,78.3452),('L006','University Hospital Area',17.4540,78.3560),('L007','North Parking',17.4530,78.3495),('L008','Sports Complex',17.4555,78.3515),('L009','South Residential Area',17.4415,78.3510),('L010','West Bus Terminal',17.4430,78.3405),('L011','Technology Park',17.4570,78.3440),('L012','East Residential Area',17.4580,78.3590)]
ROADS=[('R001','Campus Main Road'),('R002','North Connector'),('R003','Hospital Road'),('R004','Market Road'),('R005','Hostel Road'),('R006','Sports Road'),('R007','East Connector'),('R008','West Connector')]
SPECIALTIES=['Emergency Medicine','Trauma','Cardiology','Burn Care']
HOSPITALS=[('H001','CityCare Hospital','Emergency Medicine',42,18,'L006'),('H002','Metro Trauma Centre','Trauma',35,9,'L004'),('H003','HeartFirst Centre','Cardiology',24,7,'L006'),('H004','Sunrise Burn Unit','Burn Care',20,5,'L005'),('H005','Community Emergency Hospital','Emergency Medicine',30,12,'L011')]
STATIONS=[('S001','Central Emergency Station','L001'),('S002','North Response Unit','L007'),('S003','City Junction Response Centre','L004'),('S004','Hospital Rapid Response Unit','L006')]
AMBULANCES=[('A001','Ambulance 01','Available','Advanced Life Support','S001','L001'),('A002','Ambulance 02','Available','Basic Life Support','S002','L007'),('A003','Ambulance 03','Dispatched','Advanced Life Support','S004','L006'),('A004','Ambulance 04','Available','Advanced Life Support','S003','L004'),('A005','Ambulance 05','Available','Basic Life Support','S001','L001'),('A006','Ambulance 06','Maintenance','Advanced Life Support','S002','L007')]
RESPONDERS=[('P001','Central Emergency Team','Paramedic','S001',['Emergency Medicine','Trauma']),('P002','North Response Team','Paramedic','S002',['Emergency Medicine','Burn Care']),('P003','Hospital Rapid Response','Emergency Physician','S004',['Emergency Medicine','Cardiology']),('P004','Trauma Response Team','Trauma Specialist','S003',['Trauma']),('P005','Cardiac Response Team','Paramedic','S004',['Cardiology','Emergency Medicine'])]
CONNECTIONS=[('L001','L002','R001',1.1,3),('L002','L003','R005',1.4,4),('L002','L007','R002',1.0,3),('L007','L008','R006',1.2,4),('L008','L006','R003',1.8,5),('L001','L004','R004',1.5,4),('L004','L005','R004',1.0,3),('L004','L006','R003',2.4,7),('L003','L006','R003',1.6,5),('L005','L006','R003',2.0,6),('L002','L008','R006',1.7,5),('L005','L009','R004',1.6,5),('L009','L010','R008',1.9,6),('L010','L004','R008',2.0,6),('L006','L012','R007',1.4,4),('L008','L012','R007',1.3,4),('L011','L002','R002',2.1,6),('L011','L010','R008',2.2,7)]

def seed():
    driver=get_driver()
    try:
        create_schema(driver)
        with driver.session() as session:
            for x in SPECIALTIES: session.run('MERGE (s:Specialty {name:$name})',name=x)
            for i,n,lat,lon in LOCATIONS: session.run('MERGE (l:Location {id:$id}) SET l.name=$name,l.latitude=$lat,l.longitude=$lon',id=i,name=n,lat=lat,lon=lon)
            for i,n in ROADS: session.run('MERGE (r:Road {id:$id}) SET r.name=$name',id=i,name=n)
            for a,b,r,d,t in CONNECTIONS: session.run('MATCH (x:Location {id:$a}),(y:Location {id:$b}),(road:Road {id:$r}) MERGE (x)-[c:CONNECTED_TO]-(y) SET c.distance_km=$d,c.travel_time_min=$t MERGE (x)-[:USES_ROAD]->(road) MERGE (y)-[:USES_ROAD]->(road)',a=a,b=b,r=r,d=d,t=t)
            for i,n,s,cap,beds,l in HOSPITALS: session.run('MERGE (h:Hospital {id:$id}) SET h.name=$name,h.capacity=$cap,h.available_beds=$beds WITH h MATCH (s:Specialty {name:$specialty}),(l:Location {id:$location}) MERGE (h)-[:SPECIALIZES_IN]->(s) MERGE (h)-[:LOCATED_AT]->(l)',id=i,name=n,specialty=s,cap=cap,beds=beds,location=l)
            for i,n,l in STATIONS: session.run('MERGE (s:EmergencyStation {id:$id}) SET s.name=$name WITH s MATCH (l:Location {id:$location}) MERGE (s)-[:LOCATED_AT]->(l)',id=i,name=n,location=l)
            for i,n,status,v,station,l in AMBULANCES: session.run('MERGE (a:Ambulance {id:$id}) SET a.name=$name,a.status=$status,a.vehicle_type=$vehicle WITH a MATCH (s:EmergencyStation {id:$station}),(l:Location {id:$location}) MERGE (a)-[:DISPATCHED_FROM]->(s) MERGE (a)-[:LOCATED_AT]->(l)',id=i,name=n,status=status,vehicle=v,station=station,location=l)
            for i,n,role,station,specs in RESPONDERS:
                session.run('MERGE (p:Responder {id:$id}) SET p.name=$name,p.role=$role WITH p MATCH (s:EmergencyStation {id:$station}) MERGE (p)-[:BASED_AT]->(s)',id=i,name=n,role=role,station=station)
                for sp in specs: session.run('MATCH (p:Responder {id:$id}),(s:Specialty {name:$specialty}) MERGE (p)-[:QUALIFIED_FOR]->(s)',id=i,specialty=sp)
        print('ResQGraph seed completed successfully.')
    finally: driver.close()
if __name__=='__main__': seed()
