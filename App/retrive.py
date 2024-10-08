from createvectors import *
from keys import *
from createprompt import *
from langchain.load import dumps, loads
from langchain_core.retrievers import (
    BaseRetriever,
    RetrieverOutput,
)
from langchain_core.runnables import Runnable, RunnablePassthrough
from typing import Any, Dict, Union
import os
from itertools import islice


def create_retrieval_chain(
    retriever: Union[BaseRetriever, Runnable[dict, RetrieverOutput]],
    combine_docs_chain: Runnable[Dict[str, Any], str],
) -> Runnable:
    if not isinstance(retriever, BaseRetriever):
        retrieval_docs: Runnable[dict, RetrieverOutput] = retriever
    else:
        retrieval_docs = (lambda x: x["input"]) | retriever

    retrieval_chain = (
        RunnablePassthrough.assign(
            context=retrieval_docs.with_config(run_name="retrieve_documents"),
        ).assign(answer=combine_docs_chain)
    ).with_config(run_name="retrieval_chain")

    return retrieval_chain

def getRetriever(vdb):
    retriever = vdb.as_retriever(search_type = "mmr")
    return retriever

def getVDB(name = "HR"):
    if not os.path.exists(f"./App/Data/Vectors/databases/{name}"):
        print("this directory doens't exist")
        return
    vdb = Chroma(persist_directory = f'./App/Data/Vectors/databases/{name}',embedding_function=OpenAIEmbeddings())
    return vdb

def listVDB(names:list[str]):
    vdb = Chroma(persist_directory = f'./App/Data/Vectors/databases/{names[0]}',embedding_function=OpenAIEmbeddings())
    for i in islice(names, 1, None):
        temp = Chroma(persist_directory = f'./App/Data/Vectors/databases/{i}',embedding_function=OpenAIEmbeddings())
        data = temp._collection.get(include=['documents', 'metadatas', 'embeddings'])
        vdb._collection.add(
            embeddings= data['embeddings'],
            documents=data['documents'],
            metadatas=data['metadatas'],
            ids=data['ids']
        )
    return vdb

def allRetrieve(names:list[str]):
    return listVDB(names).as_retriever(search_type = 'mmr')

def raptRetrieve():
    retriever = getVDB().as_retriever(search_type = "mmr")
    return retriever

def fusion(results: list[list], k = 60):
    fused_scores = {}
    
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0

            previous_score = fused_scores[doc_str]

            fused_scores[doc_str] += 1/(rank+k)
    
    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key = lambda x: x[1], reverse = True)
    ]

    return reranked_results

def union(docs: list[list]):
    flattened = [dumps(doc) for sublist in docs for doc in sublist]
    unique = list(set(flattened))

    return [loads(doc) for doc in unique]

#retv = getRetriever(getVDB())
#print(retv.invoke("来晚了咋办"))

#vdb = getVDB()
#vdb.delete_collection()