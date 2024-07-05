from generate import *

q_a_pairs = ""
test= []
store = {}
test_id = "123"
while True:
    print("请输入您的问题：")
    question = input()
    #answer = normalGen(question)
    answer = genHist(question, test_id, store)
    for chunk in answer:
        if answer_chunk := chunk.get("answer"):
            print(f"{answer_chunk}", end = "")