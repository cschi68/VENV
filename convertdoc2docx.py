import os
import subprocess

def convert_doc_to_docx(input_dir, output_dir):
    # 確保輸出目錄存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 取得所有 .doc 檔案（排除 .docx）
    files = [f for f in os.listdir(input_dir) if f.endswith(".doc") and not f.endswith(".docx")]
    
    if not files:
        print("✅ 沒有發現需要轉換的 .doc 檔案。")
        return

    print(f"找到 {len(files)} 個 .doc 檔案，準備開始轉換...")

    for file_name in files:
        input_path = os.path.join(input_dir, file_name)
        
        # 呼叫 LibreOffice 指令進行轉檔
        # --headless: 不啟動圖形介面
        # --convert-to docx: 指定目標格式
        cmd = [
            "libreoffice", "--headless",
            "--convert-to", "docx",
            input_path,
            "--outdir", output_dir
        ]
        
        print(f"正在轉換: {file_name} ...")
        try:
            # 執行指令
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"成功: {file_name} -> .docx")
        except subprocess.CalledProcessError as e:
            print(f"❌ 轉換失敗 {file_name}: {e}")

if __name__ == "__main__":
    # 請根據你的實際目錄修改路徑
    DATA_DIR = "./data" 
    OUTPUT_DIR = "./data_docx"
    
    convert_doc_to_docx(DATA_DIR, OUTPUT_DIR)
    print("\n🎉 所有轉換任務已完成！")