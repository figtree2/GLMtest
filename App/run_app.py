from generate import *


def run_app(question, store, test_id):
    #answer, store = genHist(question, test_id, store)
    #answer, store = normalGen(question)
    answer = multiGen(question)
    
    return answer

#test_id = "123"
#store = {}
#while(True):
#    question = input()
#    answer = multiGen(question)
#    for chunk in answer:
#        print(f"{chunk}", end = "", flush = True)
    #print(normalGen(question))
    #answer = genHist(question, test_id, store)
    #for chunk in answer:
    #    if answer_chunk := chunk.get("answer"):
    #        print(f"{answer_chunk}", end = "", flush = True)
#    print("")
