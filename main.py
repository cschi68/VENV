from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings

import os
print("目前程式執行的位置：", os.getcwd())
print("data 資料夾是否存在：", os.path.exists("data"))
# os.environ["OLLAMA_NUM_GPU"] = "0"

def build_vector_db():
    # 1. 讀取 PDF (把 PDF 檔案路徑填對)
    loader = PyPDFLoader("data/test.pdf")
    documents = loader.load()
    print(f"成功讀取 PDF，共 {len(documents)} 頁")

    # 2. 切分文字 (Chunking)
    # 針對 0.5B 模型，切小一點效果比較好
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400,    # 從 200 增加到 500
    chunk_overlap=80,  # 增加重疊，確保語義不中斷
    length_function=len,
    is_separator_regex=False)
    
    chunks = text_splitter.split_documents(documents)
    print(f"文字已切分為 {len(chunks)} 個碎片")

    # 3. 變成向量並存入 ChromaDB (Embedding)
    # 使用 nomic 模型，這在 2GB 顯存上很穩
    # model_name = "BAAI/bge-small-zh-v1.5"
    # embeddings = HuggingFaceBgeEmbeddings(
    #    model_name=model_name,
    #    model_kwargs={'device': 'cpu'} # 顯式指定 CPU
    #)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    # embeddings = OllamaEmbeddings(model="bge-m3")
    
    # persist_directory 會把資料存到硬碟的 db 資料夾
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="./db"
    )
    print("向量資料庫建置完成，已存入 ./db 資料夾")
    print(chunks[0].page_content)

if __name__ == "__main__":
    build_vector_db()