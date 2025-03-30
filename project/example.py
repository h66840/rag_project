from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase
from llama_index.core.settings import Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, text
from sqlalchemy.orm import Session
import os
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10802"
os.environ["HTTPS_PROXY"]= "http://127.0.0.1:10802"
# 连接数据库
def create_sample_database():
    # 连接数据库
    engine = create_engine("mysql+pymysql://root:200220lhy@localhost:3306/chikawaka")
    return engine


def setup_llama_index_sql():
    # 初始化数据库连接
    engine= create_sample_database()
    sql_database = SQLDatabase(engine)

    # 配置 OpenAI LLM
    
    
    
    # 配置本地 embedding 模型
    # embed_model = HuggingFaceEmbedding(
    #     model_name="shibing624/text2vec-base-chinese",
    #     cache_folder="./models"  # 指定本地缓存目录
    # )
    # changing the global default
    Settings.embed_model = OpenAIEmbedding()
    # 设置全局配置
    Settings.llm = llm
    # Settings.embed_model = embed_model
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20

    # 创建查询引擎
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["finance"]
    )

    return engine,query_engine

def display_all_products(engine):
    print("\n=== 数据库中的产品示例 ===")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM finance"))
        for row in result:
            print(f"ID: {row.id}, 名称: {row.name}, 类别: {row.category}, 价格: {row.price}, 库存: {row.stock}")

def main():
    # 初始化数据库和查询引擎
    engine,query_engine = setup_llama_index_sql()
    
    # 插入示例数据（第一次运行时取消注释）
    #insert_sample_data(engine, products)

    # 显示所有产品
    # display_all_products(engine)

    # 示例查询
    queries = [
        "这个公司是在赚钱还是在亏钱"
    ]
    
    print("\n=== 查询测试 ===")
    for query in queries:
        print(f"\n查询: {query}")
        response = query_engine.query(query)
        print(f"响应: {response}")

if __name__ == "__main__":
    main()

