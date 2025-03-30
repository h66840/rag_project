from typing import List
from datasets import load_dataset
import random

# dataset = load_dataset(path="/Users/plastic/Documents/code/datasets/allenai___qasper",)

# train_dataset = dataset["train"]
# validation_dataset = dataset["validation"]
# test_dataset = dataset["test"]

# # 随机选择1000个样本
# random.seed(42)

# train_sampled_indices = random.sample(range(len(train_dataset)), 800)
# train_samples = [train_dataset[i] for i in train_sampled_indices]

# test_sampled_indices = random.sample(range(len(test_dataset)), 80)
# test_samples = [test_dataset[i] for i in test_sampled_indices]

# def get_full_text(sample: dict) -> str:
#     """
#     :param dict sample: the row sample from QASPER
#     """
#     title = sample["title"]
#     abstract = sample["abstract"]
#     sections_list = sample["full_text"]["section_name"]
#     paragraph_list = sample["full_text"]["paragraphs"]
#     combined_sections_with_paras = ""
#     if len(sections_list) == len(paragraph_list):
#         combined_sections_with_paras += title + "\t"
#         combined_sections_with_paras += abstract + "\t"
#         for index in range(0, len(sections_list)):
#             combined_sections_with_paras += str(sections_list[index]) + "\t"
#             combined_sections_with_paras += "".join(paragraph_list[index])
#         return combined_sections_with_paras

#     else:
#         print("Not the same number of sections as paragraphs list")

# def get_questions(sample: dict) -> List[str]:
#     questions_list = sample["qas"]["question"]
#     return questions_list

# doc_qa_dict_list = []

# for train_sample in train_samples:
#     full_text = get_full_text(train_sample)
#     questions_list = get_questions(train_sample)
#     local_dict = {"paper": full_text, "questions": questions_list}
#     doc_qa_dict_list.append(local_dict)

# print(len(doc_qa_dict_list))

# import pandas as pd
# df = pd.DataFrame(doc_qa_dict_list)
# df.to_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/train.csv")

eval_doc_qa_answer_list = []


# Utility function to extract answers from the dataset
def get_answers(sample: dict) -> List[str]:
    """
    :param dict sample: the row sample from the train split of QASPER
    """
    final_answers_list = []
    answers = sample["qas"]["answers"]
    for answer in answers:
        local_answer = ""
        types_of_answers = answer["answer"][0]
        if types_of_answers["unanswerable"] == False:
            if types_of_answers["free_form_answer"] != "":
                local_answer = types_of_answers["free_form_answer"]
            else:
                local_answer = "Unacceptable"
        else:
            local_answer = "Unacceptable"

        final_answers_list.append(local_answer)

    return final_answers_list

# for test_sample in test_samples:
#     full_text = get_full_text(test_sample)
#     questions_list = get_questions(test_sample)
#     answers_list = get_answers(test_sample)
#     local_dict = {
#         "paper": full_text,
#         "questions": questions_list,
#         "answers": answers_list,
#     }
#     eval_doc_qa_answer_list.append(local_dict)

# Save eval data as a csv
import pandas as pd

# df_test = pd.DataFrame(eval_doc_qa_answer_list)
# df_test.to_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/test.csv")

# The Rag Eval test data can be found at the below dropbox link
# https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0

from llama_index.core import SimpleDirectoryReader
import os
import openai
from llama_index.finetuning.cross_encoders.dataset_gen import (
    generate_ce_fine_tuning_dataset,
    generate_synthetic_queries_over_documents,
) 

from llama_index.finetuning.cross_encoders import CrossEncoderFinetuneEngine
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10802"
os.environ["HTTPS_PROXY"]= "http://127.0.0.1:10802"
os.environ["OPENAI_API_KEY"] = "sk-WXcy8xtOxqH7hWC0wfprvFUVjrnifKngp6XZ5wLrUD0Sc4xc"
openai.api_key = os.environ["OPENAI_API_KEY"]

from llama_index.core import Document

final_finetuning_data_list = []

# for paper in doc_qa_dict_list:
#     questions_list = paper["questions"]
#     documents = [Document(text=paper["paper"])]
#     local_finetuning_dataset = generate_ce_fine_tuning_dataset(
#         documents=documents,
#         questions_list=questions_list,
#         max_chunk_length=256,
#         top_k=5,
#     )
#     final_finetuning_data_list.append(local_finetuning_dataset)
#print(len(final_finetuning_data_list))
# df_finetuning_data = pd.DataFrame(final_finetuning_data_list)
# df_finetuning_data.to_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/finetuning_data.csv")
# import ast
# df_test = pd.read_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/qasper/0.3.0/test.csv",index_col=0)
# df_test["question"] = df_test["questions"].apply(lambda x: ast.literal_eval(x))
# df_test["answer"] = df_test["answers"].apply(lambda x: ast.literal_eval(x))
# print("length of test data: ",len(df_test))
# from llama_index.finetuning.cross_encoders.dataset_gen import (
#     CrossEncoderFinetuningDatasetSample,
# )
# finetune_df = pd.read_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/qasper/0.3.0/fine_tuning.csv",index_col=0)
# finetuning_dataset = finetune_df.to_dict(orient="records")
# finetuning_dataset_list = []
# for item in finetuning_dataset:
#     finetuning_dataset_list.append(CrossEncoderFinetuningDatasetSample(**item))
# from sentence_transformers import SentenceTransformer

# finetune_engine = CrossEncoderFinetuneEngine(
#     dataset=finetuning_dataset_list,epochs=2,batch_size=8
# )
# finetune_engine.finetune()

# attach to the same event-loop
import nest_asyncio

nest_asyncio.apply()

# Load Reranking Dataset
import pandas as pd
import ast

df_reranking = pd.read_csv("/Users/plastic/Documents/code/datasets/allenai___qasper/qasper/0.3.0/reranking_test.csv", index_col=0)
df_reranking["questions"] = df_reranking["questions"].apply(ast.literal_eval)
df_reranking["context"] = df_reranking["context"].apply(ast.literal_eval)
print(f"Number of papers in the reranking eval dataset:- {len(df_reranking)}")

print(df_reranking["paper"][25])

from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,Response
from llama_index.core.retrievers import VectorContextRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core import Settings

Settings.chunk_size = 256

rerank_base = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-12-v2",top_n=3
)
rerank_finetuned = SentenceTransformerRerank(
    model="/Users/plastic/Documents/code/exp_finetune",top_n=3
)
without_reranker_hits = 0
base_reranker_hits = 0
finetuned_reranker_hits = 0
total_number_of_context = 0
import tqdm
for index,row in tqdm.tqdm(df_reranking.iterrows(),total=len(df_reranking),desc="Processing papers"):
    paper = row["paper"]
    if pd.isna(paper):
        continue
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    context_list = row["context"]

    assert len(query_list) == len(context_list)
    vector_index = VectorStoreIndex.from_documents(documents)
    # retriever_without_reranker = vector_index.as_query_engine(
    #     similarity_top_k=3,response_mode="no_text"
    # )
    retriever_base_reranker = vector_index.as_retriever(
        similarity_top_k=3,
        node_postprocessors=[rerank_base],
        respense_mode="no_text"
    )
    retriever_finetuned_reranker = vector_index.as_retriever(
        similarity_top_k=3,
        node_postprocessors=[rerank_finetuned],
        respense_mode="no_text"
    )
    for index in range(0,len(query_list)):
        query = query_list[index]
        context = context_list[index]
        total_number_of_context += 1
        # response_without_reranker = retriever_without_reranker.query(query)
        # without_ranker_nodes = response_without_reranker.source_nodes

        # for node in without_ranker_nodes:
        #     if context in node.node.text or node.node.text in context:
        #         without_reranker_hits += 1
        
        with_base_reranker_nodes = retriever_base_reranker.retrieve(query)

        for node in with_base_reranker_nodes:
            if context in node.node.text or node.node.text in context:
                base_reranker_hits += 1

        with_finetuned_reranker_nodes = retriever_finetuned_reranker.retrieve(query)
        for node in with_finetuned_reranker_nodes:
            if context in node.node.text or node.node.text in context:
                finetuned_reranker_hits += 1
        
        # assert(
        #     len(with_base_reranker_nodes) == len(with_finetuned_reranker_nodes)
        #     # == len(without_ranker_nodes) == 3
        # )

# result
without_reranker_scores = [without_reranker_hits]
base_reranker_scores = [base_reranker_hits]
finetuned_reranker_scores = [finetuned_reranker_hits]
reranker_eval_dict = {
    "Metrics": "Hits",
    "OpenAI_Embeddins": without_reranker_scores,
    "Base_cross_encoder": base_reranker_scores,
    "Finetuned_cross_encoder": finetuned_reranker_scores,
    "Total Relevant Context": total_number_of_context,
}

df_reranker_eval_results = pd.DataFrame(reranker_eval_dict)
df_reranker_eval_results.to_csv(
    "/Users/plastic/Documents/code/datasets/allenai___qasper/qasper/0.3.0/reranker_eval_results.csv"
)