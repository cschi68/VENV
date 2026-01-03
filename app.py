import streamlit as st
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# import os 
# os.environ["OLLAMA_NUM_GPU"] = "0"

st.title("🤖 輕量級 PDF 助手 (Qwen 0.5B)")

@st.cache_resource
def init_rag():
    # 1. 向量庫與 Embedding
    #model_name = "BAAI/bge-small-zh-v1.5"
    #embeddings = HuggingFaceBgeEmbeddings(
    #    model_name=model_name,
    #    model_kwargs={'device': 'cpu'} # 顯式指定 CPU
    #)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    # embeddings = OllamaEmbeddings(model="bge-m3",num_gpu=0)
    
    vector_db = Chroma(persist_directory="./db", embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 2})

    # 2. 模型
    # llm = OllamaLLM(model="qwen2.5:0.5b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="qwen2.5:1.5b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="qwen3:0.6b",temperature=0,num_ctx=2048)
    llm = OllamaLLM(model="qwen3:1.7b")

    # llm = OllamaLLM(model="deepseek-coder:1.3b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="deepseek-r1:1.5b")

    # 3. 建立 Prompt 模板 (讓 AI 根據資料回答)
    template = """你是一個專業的助手。請根據以下提供的資料來回答問題。
    如果資料中沒有相關內容，請誠實回答「我不知道」，不要胡扯。

    資料內容:
    {context}

    問題: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. 建立 RAG 鏈 (LCEL 寫法，取代舊的 RetrievalQA)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

bot = init_rag()

# 聊天介面
if user_input := st.chat_input("問我關於 PDF 的問題"):
    st.chat_message("user").write(user_input)
    with st.spinner("AI 正在思考..."):
        # 呼叫新版的 Chain
        response = bot.invoke(user_input)
        st.chat_message("assistant").write(response)