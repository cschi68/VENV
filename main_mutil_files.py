import os
import json
from langchain_community.document_loaders import Docx2txtLoader # 換成這個
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma

# --- 設定與之前相同 ---
DATA_DIR = "./data_docx"
DB_DIR = "./db_bge_word"  # 建議換個名字區分
RECORD_FILE = "processed_files_word.json"

# 初始化 BGE (CPU)
model_name = "BAAI/bge-small-zh-v1.5"
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

def main():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            processed_files = set(json.load(f))
    else:
        processed_files = set()

    # 修改為掃描 .docx 檔案
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".docx")]
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        print("✅ 所有 Word 檔案皆已索引。")
        return

    # Word 檔案通常段落較長，建議 chunk_size 可以稍微調大一點
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
    
    for i, file_name in enumerate(new_files):
        print(f"[{i+1}/{len(new_files)}] 處理 Word 中: {file_name}")
        try:
            # 1. 使用 Word 載入器
            loader = Docx2txtLoader(os.path.join(DATA_DIR, file_name))
            docs = loader.load()
            
            # 2. 切分文字
            chunks = text_splitter.split_documents(docs)
            
            # 3. 存入 ChromaDB
            if not os.path.exists(DB_DIR):
                vector_db = Chroma.from_documents(
                    documents=chunks, embedding=embeddings, persist_directory=DB_DIR
                )
            else:
                vector_db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
                vector_db.add_documents(chunks)

            processed_files.add(file_name)
            with open(RECORD_FILE, "w") as f:
                json.dump(list(processed_files), f)
                
        except Exception as e:
            print(f"❌ 檔案 {file_name} 發生錯誤: {e}")

    print(f"🎉 Word 索引建置完成！路徑: {DB_DIR}")

if __name__ == "__main__":
    main()