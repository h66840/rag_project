from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core.evaluation import PairwiseComparisonEvaluator
from llama_index.core.evaluation.eval_utils import (
    get_responses,get_results_df
)

import os
import pandas as pd
import openai
import ast
# load data
df_test = pd.read_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/qasper/0.3.0/test.csv",index_col=0)
df_test["questions"] = df_test["questions"].apply(lambda x: ast.literal_eval(x))
df_test["answers"] = df_test["answers"].apply(lambda x: ast.literal_eval(x))
print("number of papers: ",len(df_test))
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10802"
os.environ["HTTPS_PROXY"]= "http://127.0.0.1:10802"
os.environ["OPENAI_API_KEY"] = "sk-WXcy8xtOxqH7hWC0wfprvFUVjrnifKngp6XZ5wLrUD0Sc4xc"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = "https://api.chatanywhere.tech/v1"
gpt4 = OpenAI(model="gpt-4",temperature=0)
evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)

pairwise_scores_list = []
no_reranker_dict_list = []

for index, row in df_test.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    reference_answers_list = row["answers"]
    number_of_accepted_queries = 0

    vector_index = VectorStoreIndex.from_documents(documents)

    query_engine = vector_index.as_query_engine(similaeity_top_k=3)

    assert len(query_list) == len(reference_answers_list)
    pairwise_local_score = 0

    for index in range(0, len(query_list)):
        query = query_list[index]
        reference = reference_answers_list[index]

        if reference != "Unacceptable":
            number_of_accepted_queries += 1

            response = str(query_engine.query(query))

            no_reranker_dict = {
                "query":query,
                "response":response,
                "reference":reference
            }
            no_reranker_dict_list.append(no_reranker_dict)

            pairwise_eval_result = evaluator_gpt4_pairwise._get_eval_result(
                query=query,
                response=response,
                reference=reference
            )
            pairwise_score = pairwise_eval_result.score
            pairwise_local_score += pairwise_score
        else:
            pass
    if number_of_accepted_queries > 0:
        avg_pairwise_local_score = (
            pairwise_local_score / number_of_accepted_queries
        )
        pairwise_scores_list.append(avg_pairwise_local_score)
overal_pairwise_score = sum(pairwise_scores_list)/len(pairwise_scores_list)

df_response = pd.DataFrame(no_reranker_dict_list)
df_response.to_csv("no_reranker_dict_list.csv")

results_dict = {
    "name":["without ranker"],
    "score":[overal_pairwise_score]
}
result_df = pd.DataFrame(results_dict)
result_df.to_csv("result_df.csv")
