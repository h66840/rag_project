import os


from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# 使用gpt生成查询语句
Settings.llm = OpenAI()

# local usage
resp = OpenAI().complete("为下文查询生成SQL语句:统计每个类别的平均价格，并按降序排序")
print(resp)
#实现
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from llama_index.core.vector_stores import PineconeVectorStore
# # 加载文档
# documents = SimpleDirectoryReader("project/data").load_data()
# #创建向量存储
# vector_store = PineconeVectorStore(
#     index_name="my-index",
#     environment='us-west1-gcp'
# )
# #创建索引
# index = VectorStoreIndex.from_documents(documents,vector_store=vector_store)

# # 创建查询引擎
# query_engine = index.as_query_engine()

# #进行查询
# response = query_engine.query("这篇文章提到了哪些公司")
# print(response)



