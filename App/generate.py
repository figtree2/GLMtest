from createvectors import *
from keys import *
from retrive import *
from createprompt import *
from raptorvecs import *
from zhipuai import ZhipuAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from operator import itemgetter
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import RetrieverLike, RetrieverOutputLike
from langchain_core.runnables import RunnableBranch
from langchain_core.language_models import LanguageModelLike
from langchain.chains.combine_documents import create_stuff_documents_chain


vdb = getVDB()
retriever = getRetriever(vdb)
llm = getLLM(0.5)

def create_history_aware_retriever(
    llm: LanguageModelLike,
    retriever: RetrieverLike,
    prompt: BasePromptTemplate,
) -> RetrieverOutputLike:
    if "input" not in prompt.input_variables:
        raise ValueError(
            "Expected `input` to be a prompt variable, "
            f"but got {prompt.input_variables}"
        )

    retrieve_documents: RetrieverOutputLike = RunnableBranch(
        (
            # Both empty string and empty list evaluate to False
            lambda x: not x.get("chat_history", False),
            # If no chat history, then we just pass input to retriever
            (lambda x: x["input"]) | retriever,
        ),
        # If chat history, then we pass inputs to LLM chain, then to retriever
        prompt | llm | StrOutputParser() | retriever,
    ).with_config(run_name="chat_retriever_chain")
    return retrieve_documents

def genHist(question: str, id:str, store:dict):
    
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    template = """
            You are an AI system assistant who is designed to answer company questions from employees based on company data. Output all the information related to the topic if it can be found on the docs, regardless of whether it is specifically asked. Answer the question based only on the following context: {context}

                
            """
    q_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    history_aware_retriever = create_history_aware_retriever(llm, raptRetrieve() , prompt)
    qa_chain = create_stuff_documents_chain(llm, q_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain, 
        get_session_history, 
        input_messages_key = "input", 
        history_messages_key = "chat_history", 
        output_messages_key = "answer"
    )
    

    answer = conversational_rag_chain.stream({"input": question}, config = {"configurable": {"session_id": id}})
    return answer


def multiGen(question):
    retriever = raptRetrieve()
    template = """You are an AI language model assistant. Your task is to use different wording with same meaning to generate five different versions of the given user questions to retrieve relevant documents from a vectorstore database. By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Only output the generated queries. 请用原本问题做一些相关的问题。 问题： {question}"""
    multi = ChatPromptTemplate.from_template(template)
    generate_queries = (multi | llm | StrOutputParser() | (lambda x: x.split("\n")))

    retrieval_chain = generate_queries | retriever.map() | union

    template = """You are an AI system assistant who is designed to answer company questions from employees based on company data. Output all the information related to the topic if it can be found on the docs, regardless of whether it is specifically asked. Answer the question based only on the following context: {context}

                Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retrieval_chain,
         "question": itemgetter("question") }
         | prompt
         |llm
         |StrOutputParser()
    )

    return rag_chain.stream({"question":question})

def normalGen(question):
    template = """You are an AI system assistant who is designed to answer company questions from employees based on company data. Output all the information related to the topic if it can be found on the docs, regardless of whether it is specifically asked. Answer the question based only on the following context: {context}

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