from generate import *

q_a_pairs = ""
test= []

while True:
    question = input("请输入您的问题：")
    answer, q_a_pairs = genHist(question, q_a_pairs)
    print(answer)