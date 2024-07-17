from generate import *
import json
from langchain.memory import ChatMessageHistory

def run_app(question, store, test_id):
    answer = genHist(question, test_id, store)
    #answer = normalGen(question)
    #answer = multiGen(question)
    
    return answer

def json_to_history(messages_list):
    chat_history = ChatMessageHistory()
    for msg in messages_list:
        if msg['type'] == 'human':
            chat_history.add_user_message(msg['data'])
        elif msg['type'] == "ai":
            chat_history.add_ai_message(msg['data'])

    return chat_history

def convertJsonToHist(store):
    temp = {}
    for key, msg in store.items():
        temp[key] = json_to_history(msg)
    return temp
        

def history_to_json(history):
    messages = history.messages
    messages_dict = [{"type": messages[-1].type, "data": messages[-1].content} ]
    return json.dumps(messages_dict)

def convertHistToJson(store):
    temp = {}
    for key, msg in store.items():
        temp[key] = history_to_json(msg)
    return temp


#test_id = "123"
#store = {}
#while(True):
#    print("请输入您的问题：")
#    question = input()
    #answer = multiGen(question)
    #for chunk in answer:
    #    print(f"{chunk}", end = "", flush = True)
    #print(normalGen(question))
#    answer, store = genHist(question, test_id, store)
##    for chunk in answer:
#        if answer_chunk := chunk.get("answer"):
#            print(f"{answer_chunk}", end = "", flush = True)
#    print("")
