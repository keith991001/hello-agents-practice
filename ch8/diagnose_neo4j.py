"""探测 Neo4j Aura 上实际存在的 database 列表"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)

# SHOW DATABASES 必须在 system 数据库里跑
with driver.session(database="system") as session:
    result = session.run("SHOW DATABASES")
    print(f"{'name':<30} {'type':<10} {'default':<8} {'currentStatus':<12}")
    print("-" * 65)
    for record in result:
        print(f"{record['name']:<30} {record['type']:<10} {str(record['default']):<8} {record['currentStatus']:<12}")

driver.close()
