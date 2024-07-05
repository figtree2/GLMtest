from zhipuai import ZhipuAI
from langchain_openai import ChatOpenAI

def getClient():
    client = ZhipuAI(api_key = "b9f8ad25a244f2af05f202b357f1ee7f.5jx9fOskHQeVFaeA")
    return client

def getAPI(): 
    key = "b9f8ad25a244f2af05f202b357f1ee7f.5jx9fOskHQeVFaeA"
    return key

def getLangKey():
    key = "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"
    return key

def getLLM(temp):
    llm = ChatOpenAI(
    temperature = temp,
    model = "glm-4",
    openai_api_key = getAPI(),
    openai_api_base = "https://open.bigmodel.cn/api/paas/v4/",
    )
    return llm