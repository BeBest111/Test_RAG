# Script khởi động PrivateGPT cho môi trường kiểm thử Nhóm 11 (Windows 10, CPU)
# Yêu cầu: Ollama đang chạy (llama3.2 + nomic-embed-text), Qdrant server chạy ở cổng 6333
#   (qdrant_server\qdrant.exe) - vì Qdrant chế độ local-file không chạy được trên Windows (BUG-ENV-05)
$env:PYTHONUTF8 = "1"                 # workaround BUG-ENV-04 (launcher.py đọc index.html bằng cp1258)
$env:PYTHONIOENCODING = "utf-8"
# BUG-ENV-02: python-magic cần libmagic.dll + magic.mgc; libmagic không mở được đường dẫn có dấu tiếng Việt
$env:PATH = "C:\Users\Admin\pgpt_nhom11_magic;$env:PATH"
$env:MAGIC = "C:\Users\Admin\pgpt_nhom11_magic\magic.mgc"
$env:OPENAI_API_BASE = "http://localhost:11434/v1"
$env:OPENAI_EMBEDDING_API_BASE = "http://localhost:11434/v1"
$env:PGPT_LLM_DEFAULT = "qwen2.5:3b"
$env:PGPT_EMBEDDING_DEFAULT = "nomic-embed-text:latest"
$env:PGPT_EMBED_DIM = "768"
$env:PGPT_PROFILES = "nhom11"            # settings-nhom11.yaml: Qdrant server mode
$env:PORT = "8080"
$env:PGPT_HOME = "$PSScriptRoot\pgpt_home_nhom11"   # dữ liệu kiểm thử tách riêng
Set-Location $PSScriptRoot
# Lưu ý: tài liệu cài đặt Windows ghi "python -m private_gpt" - thiếu lệnh con "serve" (DOC-09)
.\.venv\Scripts\python.exe -m private_gpt serve
