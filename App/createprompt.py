from keys import *
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

client = getClient()
key = getAPI()
llm = getLLM(0.5)

def decomposition(question):
    template = """You are a helpful assistant that generates multiple sub-questions related to an input question. This is meant for the company Hepalink, and employees will ask questions based on their daily needs when working. \n
            Using the original text of the question, break the question down into smaller components. Only output the query texts without the number\n
            Generate multiple search queries related to: {question} \n
            Output (3 queries):"""
    
    decomp = ChatPromptTemplate.from_template(template)
    generate_queries_chain = (decomp | llm | StrOutputParser() | (lambda x: x.split("\n")))
    questions = generate_queries_chain.invoke({"question": question})
    return questions

def multiquery(question):
    template = """You are an AI language model assistant. Your task is to generate five different versions of the given user questions to retrieve relevant documents from a vectorstore database. By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Only output the generated queries. 请用原本问题做一些相关的问题。 问题： {question}"""
    multi = ChatPromptTemplate.from_template(template)
    generate_queries = (multi | llm | StrOutputParser() | (lambda x: x.split("\n")))
    return generate_queries.invoke({"question": question})


#print(multiquery("昨天没打卡有啥吗后果"))