import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

def get_driver():
    uri=os.getenv('COGNODB_URI'); username=os.getenv('COGNODB_USERNAME','cognodb'); password=os.getenv('COGNODB_PASSWORD')
    if not uri: raise RuntimeError('COGNODB_URI is not configured.')
    if not password: raise RuntimeError('COGNODB_PASSWORD is not configured.')
    return GraphDatabase.driver(uri,auth=(username,password),max_connection_pool_size=20,connection_timeout=10)

def verify_connection(driver):
    with driver.session() as session: return session.run('RETURN 1 AS ok').single()['ok']==1
