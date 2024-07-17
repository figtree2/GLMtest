from typing import Dict, List, Optional, Tuple
from keys import *

import numpy as np
import pandas as pd
import umap
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sklearn.mixture import GaussianMixture
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma




import os

os.environ['OPENAI_API_KEY'] = 'sk-proj-KBb5IeejgH01LlueVnk2T3BlbkFJjwqsHS254cciQHGRTe3D'
embd = OpenAIEmbeddings()
model = getLLM(0.2)

#performs global dimension reduction using UMAP, 
def clusterEmbedGlob(embeddings: np.ndarray, dim: int, n_neighbors: Optional[int] = None, metric:str = "cosine"):
    if n_neighbors is None:
        n_neighbors = int((len(embeddings)-1) ** 0.5)
    return umap.UMAP(n_neighbors= n_neighbors, n_components = dim, metric = metric).fit_transform(embeddings)


#Reduces dimensions locally on the embeddings using UMAP, after global has been doing already
#both these embedding methods can help look at data in different scales to pick it out
def localEmbed(embeddings: np.ndarray, dim: int, n_neighbors: int = 10, metric: str = "cosine"):
    return umap.UMAP(n_neighbors = n_neighbors, n_components = dim, metric = metric).fit_transform(embeddings)


#optimal using Bayesian Information Criterion along with Gaussian Mixture model
#calculated using a point estimate with 95% confidence intervals to characterize uncertainty
def getOpt(embeddings: np.ndarray, max_clusters:int = 50, rand_state: int = 200) -> int:
    max_clusters = min(max_clusters, len(embeddings))
    n_clusters = np.arange(1, max_clusters)
    opt = []
    for n in n_clusters:
        gm = GaussianMixture(n_components=n, random_state=rand_state)
        gm.fit(embeddings)
        opt.append(gm.bic(embeddings))
    return n_clusters[np.argmin(opt)]


#cluster embedding using only Gaussian Mixture Model, based on probability threshold of similarity
def GMM(embeddings: np.ndarray, threshold: float, random_state: int = 0):
    n_clusters = getOpt(embeddings)
    gm = GaussianMixture(n_components= n_clusters, random_state= random_state)
    gm.fit(embeddings)
    probs = gm.predict_proba(embeddings)
    labels = [np.where(prob > threshold)[0] for prob in probs]
    return labels, n_clusters


#clusters the embeddings by reducing their dimensions then locally clustering each group together
def create_clusters(embeddings:np.ndarray, dim:int, threshold:float) -> List[np.ndarray]:
    if len(embeddings) <= dim+1:
        return [np.array([0]) for _ in range(len(embeddings))]
    
    global_reduced = clusterEmbedGlob(embeddings, dim)

    global_clust, n_global_clust = GMM(global_reduced, threshold)

    all_local_clusts = [np.array([]) for _ in range(len(embeddings))]
    total_clusters = 0

    for i in range(n_global_clust):
        global_cluster_embeddings = embeddings[np.array([i in gc for gc in global_clust])]
        if(len(global_cluster_embeddings)) == 0:
            continue
        if(len(global_cluster_embeddings)) <= dim+1:
            local_clusts = [np.array([0]) for _ in global_cluster_embeddings]
            n_local_clusters = 1
        else:
            reduced_embeddings_loc = localEmbed(global_cluster_embeddings, dim)
            local_clusts, n_local_clusters = GMM(reduced_embeddings_loc, threshold)

        for j in range(n_local_clusters):
            local_cluster_embeddings = global_cluster_embeddings[np.array([j in lc for lc in local_clusts])]
            inx = np.where((embeddings == local_cluster_embeddings[:,None]).all(-1))[1]
            for idx in inx:
                all_local_clusts[idx] = np.append(all_local_clusts[idx], j+ total_clusters)
            
        total_clusters += n_local_clusters

    return all_local_clusts

#makes embeddings for each chunk
def embed(texts):
    text_embeddings = embd.embed_documents(texts)
    text_embeddings_arr = np.array(text_embeddings)
    return text_embeddings_arr

#embeds texts and then clusters them
def embedCluster(texts):
    text_embeddings_arr = embed(texts)
    cluster_labels = create_clusters(text_embeddings_arr, 10,0.1)
    df = pd.DataFrame()
    df["text"] = texts
    df["embd"] = list(text_embeddings_arr)
    df["cluster"] = cluster_labels
    return df

#formats all the text to a single string
def format(df: pd.DataFrame) -> str:
    unique = df["text"].tolist()
    return "--- --- \n --- ---".join(unique)

#transforms the text via embedding, then clustering, then summarizing
def transformTxt(texts: List[str], level:int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_clusters = embedCluster(texts)
    expanded_list = []

    for index, row in df_clusters.iterrows():
        for cluster in row["cluster"]:
            expanded_list.append({"text": row["text"], "embd": row["embd"], "cluster": cluster})

    expanded_df = pd.DataFrame(expanded_list)

    all_clust = expanded_df["cluster"].unique()

    print(f"--Generated {len(all_clust)} clusters--")

    template = """
            这是来自 Hepalink 公司的一组文本。这些数据可以是有关公司政策的文档，也可以是来自公司物流的数据。以原始语言提供文档的详细摘要. 
    
    文档{context}"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    summaries = []
    for i in all_clust:
        print("hi")
        df_cluster = expanded_df[expanded_df["cluster"] == i]
        formatted_txt = format(df_cluster)
        summaries.append(chain.invoke({"context": formatted_txt}))

    print(summaries)
    
    df_summary = pd.DataFrame({
        "summaries": summaries, 
        "level": [level] * len(summaries),
        "cluster": list(all_clust),
    })

    return df_clusters, df_summary

#recursively transforms all the text until there is one text
def recursiveTransform(texts: List[str], level:int = 1, n_levels: int = 3) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
    results = {}

    df_clusters, df_summary = transformTxt(texts, level)

    results[level] = (df_clusters, df_summary)

    unique_clusters = df_summary["cluster"].nunique()
    if level < n_levels and unique_clusters > 1:
        new_texts = df_summary["summaries"].tolist()
        next_level_results = recursiveTransform(new_texts, level + 1, n_levels)

        results.update(next_level_results)

    return results

def totxt():
    docs = os.listdir('./app/Data/Docs')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100, separators = ["\n\n",'\n'])

    allTxt = []
    for dir in docs:
        if dir.endswith('.docx'):
            try:
                txt = Docx2txtLoader(f'./app/Data/Docs/{dir}').load()[0].page_content
                split = text_splitter.split_text(txt)
                for i in split:
                    allTxt.append(i)
            except:
                continue
    return allTxt

def makeTree():
    all_texts = totxt()
    tree = recursiveTransform(all_texts, level = 1, n_levels = 3)
    return tree

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def vectordb(texts, name = ""):
    if not os.path.exists(f"./app/Data/Vectors/databases/{name}"):
        vdb = Chroma.from_texts(
            texts = texts,embedding=OpenAIEmbeddings(),
            persist_directory=f'./app/Data/Vectors/databases/{name}',
        )
    else:
        vdbt = Chroma(persist_directory = f'./App/Data/Vectors/databases/{name}',embedding_function=OpenAIEmbeddings())
        vdbt.delete_collection()
        vdb = Chroma.from_texts(
            texts = texts,embedding=OpenAIEmbeddings(),
            persist_directory=f'./app/Data/Vectors/databases/{name}',
        )
    return vdb

def makeVecs(name = ""):
    docs = makeTree()
    txt = totxt()
    for level in sorted(docs.keys()):
        summaries = docs[level][1]["summaries"].tolist()
        txt.extend(summaries)
    vectordb(txt, name)

#makeVecs("IT")
