from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import Docx2txtLoader
from zhipuai import ZhipuAI
from langchain_openai import OpenAIEmbeddings
import tiktoken
import os


from keys import *
client = getClient()
os.environ['OPENAI_API_KEY'] = 'sk-proj-KBb5IeejgH01LlueVnk2T3BlbkFJjwqsHS254cciQHGRTe3D'

def vectordb(docs, name = ""):
    if not os.path.exists("./app/Data/Vectors/databases/"):
        vdb = Chroma.from_documents(
            documents = docs,embedding=OpenAIEmbeddings(),
            persist_directory='./app/Data/Vectors/databases/',
        )
    else:
        os.remove('./app/Data/Vectors/databases/')
        vdb = Chroma.from_documents(
            documents = docs,embedding=OpenAIEmbeddings(),
            persist_directory='./app/Data/Vectors/databases/',
        )
    return vdb


def createChunks():
    docs = os.listdir('./app/Data/Docs')
    Chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 400, chunk_overlap = 60, separators = ["\n\n",'\n'])

    for dir in docs:
        if dir.endswith('.docx'):
            try:
                txt = Docx2txtLoader(f'./app/Data/Docs/{dir}')
                split = text_splitter.split_documents(txt.load())
                Chunks.extend(split)
            except:
                continue
        #elif dir.endswith('.png') or dir.endswith('.jpeg'):

    
    return Chunks

