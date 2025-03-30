import os
# define pinecone index
from pinecone import Pinecone, ServerlessSpec
import openai
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10802"
os.environ["HTTPS_PROXY"]= "http://127.0.0.1:10802"
os.environ["OPENAI_API_KEY"] = "sk-WXcy8xtOxqH7hWC0wfprvFUVjrnifKngp6XZ5wLrUD0Sc4xc"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = "https://api.chatanywhere.tech/v1"
pc = Pinecone(
    api_key="pcsk_7JMJuQ_CRTvgLHrBUwCKLgFvWodv8Ae1M1deS7cnYufb8uYurotgLejZLgHgrY7X16Xadm",
)

# Now do stuff 创建向量库
if 'myindex' not in pc.list_indexes().names():
    pc.create_index(
        name='myindex', 
        dimension=1536, 
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# connect to index
pinecone_index = pc.Index('myindex')
# OPTIONAL: delete all
# pinecone_index.delete(deleteAll=True)
from llama_index.core import StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex


# define pinecone vector index
vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index, namespace="wiki_cities"
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
vector_index = VectorStoreIndex([], storage_context=storage_context)
# dimensions are for text-embedding-ada-002
# pinecone.create_index("quickstart", dimension=1536, metric="euclidean", pod_type="p1")

# os.environ["TOEGETHER_API_KEY"] = "your-api-key"
# 定义内存数据
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
)
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()
# create city SQL table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("country", String(16), nullable=False),
)

metadata_obj.create_all(engine)
from sqlalchemy import insert

rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {"city_name": "Berlin", "population": 3645000, "country": "Germany"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)
with engine.connect() as connection:
    cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
    print(cursor.fetchall())

from llama_index.readers.wikipedia import WikipediaReader

cities = ["Toronto", "Berlin", "Tokyo"]
# wiki_docs = WikipediaReader().load_data(pages=cities)

from llama_index.core import SQLDatabase

sql_database = SQLDatabase(engine, include_tables=["city_stats"])

from llama_index.core.query_engine import NLSQLTableQueryEngine

sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"],
)


from llama_index.core import VectorStoreIndex
# Insert documents into vector index
# Each document has metadata of the city attached
# for city, wiki_doc in zip(cities, wiki_docs):
#     nodes = Settings.node_parser.get_nodes_from_documents([wiki_doc])
#     # add metadata to each node
#     for node in nodes:
#         node.metadata = {"title": city}
#     vector_index.insert_nodes(nodes)


from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores import MetadataInfo, VectorStoreInfo
from llama_index.core.query_engine import RetrieverQueryEngine

vector_store_info = VectorStoreInfo(
    content_info="articles about different cities",
    metadata_info=[
        MetadataInfo(
            name="title", type="str", description="The name of the city"
        ),
    ],
)
vector_auto_retriever = VectorIndexAutoRetriever(
    vector_index, vector_store_info=vector_store_info
)

retriever_query_engine = RetrieverQueryEngine.from_args(
    vector_auto_retriever, llm=OpenAI(model="gpt-4o")
)

from llama_index.core.tools import QueryEngineTool

sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "This tool is specifically designed to translate natural language queries into SQL queries for operating on a database table named 'city_stats'. "
        "This table contains structured data such as the name, population, and country of each city. "
        "Use this tool when you need to query the population or country of a city, or perform statistical analysis based on this data."
    ),
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=retriever_query_engine,
    description=(
        "This tool is useful for answering semantic questions about different cities. "
        "Based on vector indexing and retrieval mechanisms, it can find semantically matching information from unstructured data such as encyclopedic articles about cities, "
        "including aspects like the culture, history, and tourist attractions of a city."
    ),
)

from llama_index.core.query_engine import SQLAutoVectorQueryEngine

query_engine = SQLAutoVectorQueryEngine(
    sql_tool, vector_tool, llm=OpenAI(model="gpt-4",temperature=0)
)

response = query_engine.query(
    "what about the finance of the city with the highest population"
)
print(response)