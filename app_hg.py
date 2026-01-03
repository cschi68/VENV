import streamlit as st
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import os 
# os.environ["OLLAMA_NUM_GPU"] = "0"


    # 用於格式化檢索到的文件內容（將多個文件片段合併成一段文字供 LLM 讀取）
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

st.title("🤖 輕量級助手 (qwen3:1.7b)")

@st.cache_resource
def init_rag():
    # 1. 向量庫與 Embedding
    model_name = "BAAI/bge-small-zh-v1.5"
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'} # 顯式指定 CPU
    )
    # embeddings = OllamaEmbeddings(model="nomic-embed-text")
    # embeddings = OllamaEmbeddings(model="bge-m3",num_gpu=0)
    
    vector_db = Chroma(persist_directory="./db_bge_word", embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 4})
    # 2. 模型
    # llm = OllamaLLM(model="qwen2.5:0.5b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="qwen2.5:1.5b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="qwen3:0.6b",temperature=0,num_ctx=2048)
    llm = OllamaLLM(model="qwen3:1.7b")

    # llm = OllamaLLM(model="deepseek-coder:1.3b",temperature=0,num_ctx=2048)
    # llm = OllamaLLM(model="deepseek-r1:1.5b")

    # 3. 建立 Prompt 模板 (讓 AI 根據資料回答)
    template = """
    你現在是【核能電廠安全運作與程序規範專家】。
    你的任務是根據提供的「程序書片段」回答使用者的問題，如果資料中沒有相關內容，請誠實回答「我不知道」，不要胡扯。

    ### 執行準則：
    1. **嚴謹性**：核能安全至上。如果程序書片段中沒有明確答案，請回答：「根據目前載入的程序書資料，無法提供此問題的確切答案，請查閱原始紙本文件或詢問主管。」，絕對不可編造數值。
    2. **證據導向**：在回答時，如果資料中有提到檔案名稱或頁碼，請務必標註（例如：根據 [程序書A-01] 第12頁...）。
    3. **專業術語**：請使用專業的中文化技術術語，不要口語化。
    4. **結構化回覆**：如果答案包含步驟，請使用 1. 2. 3. 標號列出。

    ### 參考資料（Context）：
    資料內容:
    {context}

    ### 使用者問題：
    問題: {question}    
    """    
    prompt = ChatPromptTemplate.from_template(template)

    # 3. 建立 LCEL RAG 鏈
    # 我們把 retrieval 分開，以便最後能拿到原始的 docs
    # 建立一個獨立的處理鏈
    # 第一步：獲取文檔與保留問題
    map_chain = RunnableParallel({
        "context_docs": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"]
    })

    # 第二步：組合最終輸出
    # 使用 assign 逐步增加欄位，確保資料始終以 dict 格式傳遞
    full_chain = (
        map_chain 
        | RunnablePassthrough.assign(
            context=lambda x: format_docs(x["context_docs"])
        )
        | RunnablePassthrough.assign(
            answer=prompt | llm | StrOutputParser()
        )
    )
    
    return full_chain

bot = init_rag()

# 1. 初始化對話紀錄 (如果還不存在的話)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 顯示過去的對話紀錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# 聊天介面
if user_input := st.chat_input("問我關於 核能電廠緊急應變程序 的問題"):
    
    # 把使用者的話存入記憶
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    st.chat_message("user").write(user_input)
    with st.spinner("AI 正在思考..."):
        # 關鍵：這裡必須傳入 dict
        response = bot.invoke({"question": user_input})
        
        # 取得回答
        answer = response.get("answer", "無法生成回答")
        sources = response.get("context_docs", [])
        
        #
        # --- 關鍵修正點：只提取 answer 字串 ---
        full_answer = response["answer"]
        # sources = response["context"] # 這是原始的 Documents 列表
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            
            # 顯示來源
            if sources:
                with st.expander("📚 查看原始程序書來源"):
                    for doc in sources:
                        src = os.path.basename(doc.metadata.get('source', '未知'))
                        st.write(f"📄 {src}")
                        st.caption(doc.page_content[:200] + "...")
                        
        # 將 AI 的回答存入 session (只存字串，不存整個 response 物件)
        st.session_state.messages.append({"role": "assistant", "content": full_answer})