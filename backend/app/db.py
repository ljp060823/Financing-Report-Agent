from langgraph.checkpoint.mysql.aio import AIOMySQLSaver
from langchain_neo4j import Neo4jGraph
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    MYSQL_URI: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    REDIS_URI: str
    BOCHA_API_KEY: str   

    # 正确指定你的.env绝对路径
    model_config = SettingsConfigDict(
        env_file="/data/financial agent/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 关闭大小写敏感
        extra="ignore", 
    )

settings = Settings()

async def get_checkpointer():
    checkpointer = AIOMySQLSaver.from_conn_string(settings.MYSQL_URI)
    await checkpointer.setup()
    return checkpointer

# Neo4j 4.4.48 Graph实例（生产：连接池自动管理）
graph_db = Neo4jGraph(
    url=settings.NEO4J_URI,
    username=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD,
    database="neo4j"
)

embeddings = HuggingFaceEmbeddings(model_name="/data/bge-m3")

# 初始化
# graph_db.query("""
# CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
# """)
# graph_db.query("""
# CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
# """)