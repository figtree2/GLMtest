from createvectors import *
from keys import *
from createprompt import *
from langchain.load import dumps, loads


def getRetriever(vdb):
    retriever = vdb.as_retriever(search_kwargs = {"k": 5})
    return retriever

def getVDB():
    vdb = Chroma(persist_directory = './app/Data/Vectors/databases/',embedding_function=OpenAIEmbeddings())
    return vdb

def raptRetrieve():
    retriever = getVDB().as_retriever()
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


print(raptRetrieve().invoke("昨天没打卡")[0])