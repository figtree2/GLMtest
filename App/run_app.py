from generate import *


def run_app(question, store, test_id):
    answer = genHist(question, test_id, store)
    
    return answer