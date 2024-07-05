from createvectors import *
from keys import *
from retrive import *
from createprompt import *
from raptorvecs import *
from zhipuai import ZhipuAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain import hub

vdb = getVDB()
retriever = getRetriever(vdb)
llm = getLLM(0.3)

def genHist(question: str, q_a_pairs:str = ""):
    def format_qa_pair(question: str, answer):

        formatted_string = ""
        formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
        return formatted_string.strip()

    template = """
            Here is the question you need to answer:
            \n --- \n {question} \n --- \n
            
            Here is additional context relevant to the question, along with the history q_a_pairs. 
            \n --- \n {context} \n --- \n
            \n --- \n {q_a_pairs} \n --- \n

            Use the above context and any background question + answer pairs to answer the question. If the answer can't be found from the context or from old q_a_pairs, say you don't know, or ask for more clarification from the user: : \n {question}
                
               """
    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = (
            {"context": itemgetter("question") | raptRetrieve() | format_docs, "question": itemgetter("question"),
             "q_a_pairs": itemgetter("q_a_pairs")
             }
             | prompt
             | llm
             | StrOutputParser()
        )

    answer = rag_chain.invoke({"question": question, "q_a_pairs": q_a_pairs})
    q_a_pair = format_qa_pair(question, answer)
    q_a_pairs = q_a_pairs + "\n---\n" + q_a_pair
    return answer, q_a_pairs

def normalGen(question):
    template = """You are an AI system assistant who is designed to answer company questions from employees based on company data. If you don't have an exact answer from the docs, say you aren't sure and ask for more specific details from the user. Answer the question based only on the following context: {context}

                Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {
            "context": raptRetrieve() | format_docs, "question": RunnablePassthrough()
        }
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain.invoke(question)


def decomposeGen(questions, q_a_pairs = ""):
    template = """ Here is the question you need to answer:
            \n --- \n {question} \n --- \n

            Here is any available background question + answer pairs:
            \n --- \n {q_a_pairs} \n --- \n

            Here is additional context relevant to the question. If the answer can't be found from the context, say you don't know, or ask for more clarification from the user: 
            \n --- \n {context} \n --- \n

            Use the above context and any background question + answer pairs to answer the question : \n {question}

    """
    def format_qa_pair(question, answer):
        """Format Q and A pair"""

        formatted_string = ""
        formatted_string += f"Question: {question}\nAnswer: {answer}\n\n"
        return formatted_string.strip()
    
    decomp_prompt = ChatPromptTemplate.from_template(template)
    for i in questions:
        print(i)
        rag_chain = (
            {"context": itemgetter("question") | retriever, "question": itemgetter("question"),
             "q_a_pairs": itemgetter("q_a_pairs")
             }
             | decomp_prompt
             | llm
             | StrOutputParser()
        )

        answer = rag_chain.invoke({"question": i, "q_a_pairs": q_a_pairs})
        q_a_pair = format_qa_pair(i, answer)
        q_a_pairs = q_a_pairs + "\n---\n" + q_a_pair
    return answer, q_a_pairs



def generateByDec(question, q_a_pairs = ""):
    questions = decomposition(question)
    questions.append(question)
    answer, q_a_pairs = decomposeGen(questions, q_a_pairs)
    return answer, q_a_pairs

#print(generateByDec("如果我早上正常打卡，晚上工作太晚到第二天早晨，那么我第二天的打卡算不算前一天正常打卡", "")[0])
#print(normalGen("如果我早上正常打卡，晚上工作太晚到第二天早晨，那么我第二天的打卡算不算前一天正常打卡"))