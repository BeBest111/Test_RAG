"""Nội dung văn bản của báo cáo BTLSo1 (Phần 1, Phần 2 từng thành viên, Phần 3)."""

PART1 = {
    "intro": [
        "RAG (Retrieval-Augmented Generation – sinh văn bản tăng cường truy xuất) là kỹ thuật kết hợp mô hình ngôn ngữ lớn (LLM) "
        "với một kho tri thức riêng: tài liệu của người dùng được chia đoạn, mã hóa thành vector và lưu vào cơ sở dữ liệu vector; "
        "khi người dùng đặt câu hỏi, hệ thống truy xuất các đoạn liên quan nhất rồi đưa vào ngữ cảnh để LLM sinh câu trả lời có căn cứ "
        "và có thể trích dẫn nguồn. Chất lượng của một ứng dụng RAG vì vậy phụ thuộc đồng thời vào khâu nạp tài liệu, khâu truy xuất, "
        "khả năng tuân thủ ngữ cảnh của mô hình và độ tin cậy của phần mềm bao quanh.",
        "Theo yêu cầu bài tập, nhóm ưu tiên chọn một hệ thống đã được công khai trên GitHub. Sau khi so sánh các dự án RAG mã nguồn mở "
        "phổ biến (Open WebUI ~158 nghìn sao, RAGFlow ~94 nghìn sao, PrivateGPT ~57,6 nghìn sao, Kotaemon ~26 nghìn sao) với cấu hình "
        "máy của nhóm (16GB RAM, không GPU, Windows 10), nhóm chọn PrivateGPT của Zylon AI vì: (1) là một trong những dự án RAG nhiều sao "
        "nhất, có mã nguồn và tài liệu đầy đủ; (2) có cả REST API và giao diện Workbench nên kiểm thử được cả giao diện lẫn hộp đen; "
        "(3) có tài liệu đặc tả sản phẩm (PRD.md, STYLE_GUIDE.md) để thực hiện review; (4) có bộ test sẵn có để đánh giá hiện trạng; "
        "(5) các chức năng tách bạch, đủ phức tạp để phân công cho 4 thành viên. RAGFlow cần tối thiểu 16GB RAM dành riêng và 50GB đĩa "
        "nên không chạy được trên máy của nhóm.",
    ],
    "intro_table": [
        ["Tên hệ thống", "PrivateGPT (phiên bản 1.0.1) – kèm giao diện PrivateGPT Workbench"],
        ["Nguồn", "Mã nguồn mở của Zylon AI, công khai trên GitHub"],
        ["Đường link", "https://github.com/zylon-ai/private-gpt – tài liệu: https://docs.privategpt.dev"],
        ["Giấy phép", "Apache License 2.0"],
        ["Mức độ phổ biến", "~57.600 sao GitHub, 464 commit, 123 người đóng góp (tại thời điểm kiểm thử)"],
        ["Phiên bản kiểm thử", "Nhánh main, commit 42ce052 (29/10/2026)"],
        ["Quy mô mã nguồn", "~104.000 dòng Python (thư mục private_gpt) + 8.210 dòng HTML/CSS/JS (ui/index.html)"],
        ["Mục tiêu sản phẩm", "Lớp API theo chuẩn Claude/Anthropic Messages biến mô hình chạy cục bộ thành ứng dụng AI riêng tư: "
                              "hỏi đáp tài liệu có trích dẫn, công cụ web, SQL, MCP, skills…"],
    ],
    "tech_intro": "PrivateGPT không tự chạy mô hình mà kết nối tới một máy chủ suy luận tương thích OpenAI (Ollama, llama.cpp, vLLM…). "
                  "Môi trường kiểm thử của nhóm được dựng hoàn toàn cục bộ trên Windows, không dùng dịch vụ đám mây.",
    "tech_table": [
        ["Ngôn ngữ / framework", "Python 3.11, FastAPI, Uvicorn, Pydantic v2, Injector (DI)", "Xây dựng REST API, kiểm tra dữ liệu, tiêm phụ thuộc"],
        ["Khung RAG", "LlamaIndex core 0.14", "Chia đoạn, tạo chỉ mục, truy xuất, tổng hợp câu trả lời"],
        ["Vector store", "Qdrant 1.20 (chế độ server)", "Lưu và tìm kiếm vector nhúng"],
        ["Lưu trữ khác", "SQLite, docstore/indexstore dạng JSON", "Metadata, trạng thái tài liệu, skills"],
        ["LLM", "Ollama 0.40.15 – qwen2.5:3b (chính), llama3.2:3b (đối chứng)", "Sinh câu trả lời, gọi công cụ semantic_search"],
        ["Embedding", "nomic-embed-text (768 chiều)", "Mã hóa tài liệu và câu hỏi thành vector"],
        ["Phân tích tài liệu", "pypdf, python-docx, python-magic (libmagic)…", "Đọc PDF/DOCX/MD/TXT, nhận dạng MIME"],
        ["Giao diện", "HTML/CSS/JavaScript thuần (1 file index.html), localStorage", "Workbench: chat, Context, Settings, API Debugger"],
        ["Công cụ kiểm thử của nhóm", "pytest 9.2, Playwright + Microsoft Edge, httpx, openpyxl", "Unit test, test UI tự động, test API, báo cáo"],
    ],
    "func_intro": "Theo README và tài liệu PRD, hệ thống cung cấp các nhóm chức năng chính sau:",
    "functions": [
        ("Nạp tài liệu (Ingestion): ", "POST /v1/artifacts/ingest nhận file base64, văn bản hoặc URI; hỗ trợ PDF, DOCX, PPTX, MD, CSV, JSON…; "
                                       "tài liệu được nhóm theo collection."),
        ("Quản lý tài liệu: ", "liệt kê (/v1/artifacts/list), xem nội dung (/v1/artifacts/content, /chunked-content), xóa (/v1/artifacts/delete)."),
        ("Hỏi đáp RAG có trích dẫn: ", "POST /v1/messages với công cụ semantic_search_v1 và tool_context; câu trả lời có thẻ trích dẫn trỏ tới đoạn nguồn."),
        ("Hội thoại & mô hình: ", "hội thoại nhiều lượt, streaming SSE, đếm token, kiểm tra request, chọn mô hình từ /v1/models."),
        ("Giao diện Workbench: ", "Context (Documents, Databases, Web, MCP, Skills, Custom Tools), Chat, Settings, API Debugger."),
        ("Chức năng mở rộng (ngoài phạm vi kiểm thử): ", "truy vấn SQL, phân tích CSV bằng code sandbox, web search/fetch, MCP, skills, custom tools."),
    ],
    "rag_flow": "Luồng xử lý RAG: (1) người dùng tải tài liệu → server kiểm tra kích thước/định dạng/MIME → phân tích và chia đoạn → "
                "tạo embedding → lưu Qdrant; (2) người dùng hỏi → LLM quyết định gọi semantic_search với truy vấn → server truy xuất "
                "top-k đoạn (k=32, ngưỡng tương đồng 0,4) trong phạm vi collection → LLM sinh câu trả lời và gắn mã trích dẫn [ID] → "
                "server chuyển thành thẻ <citation> → giao diện hiển thị nút số trích dẫn có popup đoạn nguồn.",
    "qa_status": [
        "Về tài liệu: dự án có README, bộ tài liệu Fern (cài đặt, cấu hình, API guide), hợp đồng OpenAPI và hai tài liệu đặc tả cho "
        "giao diện là PRD.md (product requirements – 1.000 dòng, 23 tiêu chí chấp nhận MVP) và STYLE_GUIDE.md. Tuy nhiên chưa có tài liệu "
        "đặc tả yêu cầu dạng SRS/use case, yêu cầu không có mã định danh và hoàn toàn thiếu yêu cầu phi chức năng; vì vậy nhóm lập thêm "
        "tài liệu đặc tả bổ sung (03_MinhChung/DacTa_YeuCau_BoSung_Nhom11.docx).",
        "Về kiểm thử: dự án có 217 file test với khoảng 2.074 hàm test (pytest), CI GitHub Actions (tests.yml) chạy toàn bộ test kèm "
        "đo coverage, có ruff/mypy. Nhưng CI chỉ chạy trên ubuntu-latest, các test route dùng LLM giả lập (mock), không có test giao diện "
        "tự động cho Workbench, không có test hiệu năng/đồng thời và rất ít test cho nhánh lỗi (negative path). Đây chính là các khoảng "
        "trống mà nhóm tập trung kiểm thử.",
    ],
    "qa_table": [
        ["Tài liệu yêu cầu", "PRD.md, STYLE_GUIDE.md, docs Fern, OpenAPI", "Có nhưng thiếu NFR, thiếu ID, nhiều mâu thuẫn (16 lỗi tài liệu)"],
        ["Unit/integration test", "217 file, ~2.074 test, pytest", "Phủ tốt happy path; thiếu negative test"],
        ["CI/CD", "GitHub Actions: tests.yml, fern-check, release-please", "Chỉ Ubuntu → không phát hiện lỗi Windows (ENV-01..06)"],
        ["Kiểm thử giao diện", "Không có (chỉ 1 test kiểm tra mount /ui)", "Nhóm bổ sung 31 test UI tự động bằng Playwright"],
        ["Hiệu năng / đồng thời", "Không có", "Nhóm bổ sung test tải và test nạp đồng thời → phát hiện mất dữ liệu"],
        ["Chất lượng câu trả lời RAG", "Không có bộ đánh giá", "Nhóm bổ sung bộ câu hỏi có đáp án, test hallucination, injection, trích dẫn"],
        ["Phân tích tĩnh", "ruff, mypy/ty trong dev dependencies", "Có, nhưng không phát hiện lỗi logic (vd. return thay vì continue)"],
    ],
    "install": [
        "Nhóm cài đặt đúng theo hướng dẫn chính thức cho Windows (uv sync --frozen --extra core) và Ollama. Quá trình cài đặt phát hiện "
        "6 lỗi môi trường khiến hệ thống không thể khởi động trên Windows nếu chỉ làm theo tài liệu. Để vẫn kiểm thử được mã nguồn gốc, "
        "nhóm không sửa bất kỳ dòng mã nào của dự án mà chỉ xử lý ở tầng môi trường: cài bổ sung gói, đặt biến môi trường, thêm module "
        "shim cho fcntl và chạy Qdrant ở chế độ server thông qua một profile cấu hình riêng (settings-nhom11.yaml). Toàn bộ quy trình được "
        "đóng gói trong script run_nhom11.ps1.",
        "Ban đầu nhóm dùng mô hình llama3.2 (3B) theo gợi ý phổ biến, nhưng mô hình này gọi sai công cụ semantic_search nên RAG không "
        "hoạt động (lỗi BUG-15). Nhóm bổ sung mô hình qwen2.5:3b hỗ trợ gọi công cụ tốt hơn làm mô hình chính và giữ llama3.2 để đối chứng.",
    ],
    "review_intro": [
        "Nhóm thực hiện review theo hình thức inspection: mỗi thành viên đọc trước tài liệu theo checklist (18/10 – 20/10/2026), sau đó "
        "họp review chung ngày 21/10/2026 và chốt kết quả ngày 25/10/2026. Vai trò: Nguyễn Minh Tiến – điều phối (moderator), Bùi Văn Mạnh – "
        "thư ký, Nguyễn Bá Quang Vinh và Vũ Đức Duy – reviewer. Tài liệu được rà soát: PRD.md, STYLE_GUIDE.md, các trang tài liệu cài đặt/API "
        "và OpenAPI. Checklist gồm các nhóm tiêu chí: tính đầy đủ, tính nhất quán, tính rõ ràng, tính kiểm thử được, tính khả thi, tổ chức tài "
        "liệu, truy vết, yêu cầu phi chức năng và khả năng sử dụng.",
    ],
    "review_conclusion": "Nhận xét chung: tài liệu của PrivateGPT mô tả chức năng khá chi tiết và có tiêu chí chấp nhận kiểm chứng được, "
                         "nhưng có nhiều mâu thuẫn giữa các tài liệu (URL mặc định, cơ chế xác thực, Thinking button, mã lỗi 422/400, "
                         "ví dụ multipart), thiếu hoàn toàn yêu cầu phi chức năng và đặc tả xử lý lỗi, và hướng dẫn cài đặt Windows "
                         "không chạy được. Các thiếu sót này đã được kiểm chứng lại bằng kiểm thử thực tế (ví dụ BB_TIEN_08, BB_TIEN_22).",
    "plan": [
        "Mục tiêu kiểm thử là đánh giá 4 chức năng cốt lõi của chuỗi nghiệp vụ RAG: nạp tài liệu → quản lý tài liệu → hỏi đáp có trích dẫn → "
        "quản lý hội thoại/cấu hình. Mỗi thành viên thực hiện đủ các mức: kiểm thử giao diện (tự động bằng Playwright, có ảnh chụp), kiểm thử "
        "đơn vị (pytest – white-box), kiểm thử hộp đen API (phân hoạch tương đương, giá trị biên, bảng quyết định, đoán lỗi) và ít nhất một "
        "nội dung lựa chọn thêm (kiểm thử tự động, bảo mật, hiệu năng, đánh giá chất lượng AI, ứng dụng công cụ AI).",
        "Dữ liệu kiểm thử là bộ tài liệu giả lập của 'Công ty TNHH Sao Mai' (chính sách nghỉ phép .md, quy định bảo mật .txt, quy trình hoàn "
        "tiền .docx, bảng giá .pdf, FAQ tiếng Anh .md) với các sự kiện có đáp án xác định để chấm tự động; cùng các file đặc biệt (rỗng, 2,7MB, "
        ".zip, PNG giả mạo). Tiêu chí kết thúc: 100% test case được thực thi, mọi lỗi có minh chứng và được truy vết tới yêu cầu.",
    ],
    "schedule": [
        ["15/10 – 16/10/2026", "Chọn chủ đề, khảo sát và chọn hệ thống PrivateGPT, phân công chức năng", "Cả nhóm"],
        ["16/10 – 17/10/2026", "Cài đặt môi trường Windows, xử lý 6 lỗi môi trường, dựng dữ liệu kiểm thử", "Mạnh, Tiến"],
        ["18/10 – 21/10/2026", "Review tài liệu đặc tả theo checklist, họp review 21/10", "Cả nhóm"],
        ["22/10 – 25/10/2026", "Review code chức năng cá nhân; viết đặc tả bổ sung; chốt review 25/10", "Từng thành viên"],
        ["26/10 – 28/10/2026", "Thiết kế test case: giao diện, đơn vị, hộp đen, hiệu năng", "Từng thành viên"],
        ["29/10 – 31/10/2026", "Thực thi kiểm thử giao diện (29–30/10) và kiểm thử đơn vị (31/10)", "Từng thành viên"],
        ["01/11 – 03/11/2026", "Thực thi kiểm thử hộp đen, bảo mật, hiệu năng, đồng thời; lập báo cáo lỗi", "Từng thành viên"],
        ["04/11 – 06/11/2026", "Kiểm thử hồi quy, chạy lại bộ test có sẵn, tổng hợp báo cáo, làm slide", "Cả nhóm"],
    ],
    "perf_comment": [
        "Nhận xét hiệu năng: API /v1/models phản hồi ổn định ~2,8 giây/request, không lỗi. Nạp văn bản nhỏ mất trung bình ~15 giây "
        "(đạt NFR-01 ≤ 30 giây). Hỏi đáp RAG trên CPU với mô hình 3B có trung vị ~68 giây/câu, lâu nhất 115 giây – không đạt NFR-03 (≤ 60 giây). "
        "Nghiêm trọng nhất là API liệt kê tài liệu dưới tải: 100 request với 20 luồng đồng thời có p95 = 67 giây và 33% request bị timeout "
        "(60 giây) – không đạt NFR-04, nguyên nhân là N+1 truy vấn và các thao tác bị tuần tự hóa. Kết hợp với lỗi mất dữ liệu khi nạp đồng "
        "thời (BUG-01), hệ thống chưa phù hợp cho nhiều người dùng cùng lúc.",
    ],
}

MEMBER_TEXT = {
    "TIEN": {
        "scope": "Chức năng nạp tài liệu là bước đầu tiên của chuỗi RAG: mọi sai sót ở đây (từ chối file hợp lệ, chấp nhận file độc hại, mất "
                 "tài liệu) đều ảnh hưởng trực tiếp tới chất lượng hỏi đáp. Phạm vi gồm API POST /v1/artifacts/ingest (đầu vào file base64, "
                 "text, URI) và thao tác Upload trên màn hình Context > Documents của Workbench.",
        "spec_review": "Đặc tả của chức năng nạp nằm rải rác ở PRD.md (mục Documents, Upload behavior), api-guide/ingestion.mdx và OpenAPI. "
                       "Yêu cầu cốt lõi (nạp qua API, base64, metadata.file_name) rõ ràng và kiểm thử được, nhưng tài liệu API lại đưa ví dụ "
                       "multipart mâu thuẫn với PRD; danh sách định dạng ghi 'loại khác đọc như text' trong khi .zip bị từ chối; không có giới "
                       "hạn kích thước/thời gian và không quy định hành vi khi nạp trùng.",
        "code_review": "Review tập trung vào ingest_router.py, ingest_service.py, artifact_input.py, ingestion_scheduler.py và ingest_helper.py. "
                       "Điểm tốt: kiểm tra base64 chặt chẽ, kiểm tra MIME thực tế bằng libmagic, xóa file tạm trong finally. Điểm yếu nghiêm trọng: "
                       "không ràng buộc ký tự cho artifact/collection, UriArtifact không có validator nên đọc được file cục bộ, giới hạn kích "
                       "thước chỉ là cảnh báo, giải mã base64 nhiều lần tốn bộ nhớ, import celery/fcntl vô điều kiện làm hỏng Windows.",
        "test_intro": "Test case được thiết kế từ đặc tả bổ sung (REQ-ING-01..04) bằng các kỹ thuật phân hoạch tương đương (định dạng hợp lệ/không "
                      "hợp lệ), phân tích giá trị biên (độ dài artifact 0/255/256, file 0 byte), đoán lỗi (MIME giả, trùng mã, multipart) và kiểm "
                      "thử bảo mật (path traversal, đọc file cục bộ).",
        "ui": "Kiểm thử giao diện được tự động hóa bằng Playwright điều khiển Microsoft Edge: kiểm tra bố cục, upload một/nhiều file qua ô chọn file, "
              "upload định dạng bị cấm và badge loại file. Mỗi test lưu ảnh chụp màn hình làm minh chứng.",
        "images": [("UI_TIEN_03", "UI_TIEN_03 – Upload file .txt thành công qua giao diện"),
                   ("UI_TIEN_05", "UI_TIEN_05 – Thông báo lỗi khi upload file .zip")],
        "unit": "Các test được viết theo kỹ thuật white-box, bao phủ các nhánh hợp lệ/không hợp lệ của hàm kiểm tra base64 và các ràng buộc Pydantic.",
        "blackbox": "Kiểm thử hộp đen gọi trực tiếp API bằng httpx (script blackbox_runner.py), chấm tự động theo mã HTTP và nội dung phản hồi.",
        "extra": [
            ("Kiểm thử tự động: ", "toàn bộ test UI, unit và API đều chạy tự động, kết quả xuất JSON/JUnit XML và được đưa thẳng vào file Excel."),
            ("Kiểm thử bảo mật: ", "phát hiện 2 lỗ hổng mức Cao – path traversal qua tên artifact/collection (BUG-03) và đọc file hệ thống "
                                  "C:\\Windows\\win.ini qua input type=uri (BUG-02)."),
            ("Kiểm thử hiệu năng & đồng thời: ", "nạp file 2,7MB vượt 600 giây (BUG-04); nạp đồng thời 6 tài liệu chỉ còn 1/6 trong danh sách "
                                                "(BUG-01 – mất dữ liệu)."),
            ("Ứng dụng công cụ AI: ", "dùng trợ lý AI (Claude) để đọc nhanh mã nguồn, gợi ý tiêu chí review và sinh khung test case; mọi kết quả "
                                     "đều được thành viên chạy lại và kiểm chứng thực tế."),
        ],
        "evaluation": [
            "Đánh giá: chức năng nạp hoạt động đúng với các định dạng phổ biến khi nạp tuần tự (.txt, .docx, .pdf, .md, văn bản, tên tiếng Việt) và "
            "kiểm tra đầu vào cơ bản tốt (file rỗng, base64 sai, type sai, độ dài biên đều bị chặn đúng). Tuy nhiên chức năng chưa sẵn sàng cho "
            "môi trường nhiều người dùng: có 2 lỗ hổng bảo mật mức Cao, mất dữ liệu khi nạp đồng thời và không xử lý được file vài MB trên CPU.",
            "Đề xuất: thêm pattern ^[A-Za-z0-9_-]{1,255}$ cho artifact/collection; chỉ cho phép URI http(s)/s3 và chặn địa chỉ nội bộ; biến "
            "max_file_size thành giới hạn cứng (HTTP 413); dùng khóa/giao dịch cho index store hoặc chuyển sang Postgres khi nạp song song; "
            "trả 409 hoặc thông tin tài liệu khi nạp trùng; cập nhật ví dụ multipart trong tài liệu.",
        ],
    },
    "VINH": {
        "scope": "Chức năng quản lý tài liệu cho phép người dùng biết hệ thống đang 'biết' những gì và loại bỏ tài liệu lỗi thời. Phạm vi gồm "
                 "GET /v1/artifacts/list, POST /v1/artifacts/delete, POST /v1/artifacts/content, /chunked-content và danh sách tài liệu, nút "
                 "Refresh, nút Delete trên màn hình Context > Documents.",
        "spec_review": "Yêu cầu liệt kê và xóa rõ ràng, kiểm thử được; yêu cầu collection cấu hình toàn cục trong Settings được mô tả tốt. Tuy nhiên "
                       "PRD coi Preview/Search là tùy chọn trong khi STYLE_GUIDE bắt buộc menu Preview/Search/Delete và trạng thái "
                       "Indexed/Processing/Failed; không đặc tả kết quả khi xóa tài liệu không tồn tại, xóa hai lần, phân trang danh sách.",
        "code_review": "Review ingest_router.py (list/delete), ingest_service.py, base_artifact_index.py, content_router.py, content_service.py và "
                       "hàm renderDocuments/deleteDocument trong index.html. Phát hiện lỗi logic 'return' thay vì 'continue' trong vòng lặp liệt kê "
                       "(ingest_service.py:187-188), xóa không idempotent (đặt lại trạng thái 'initialized'), không có phân trang, N+1 truy vấn, "
                       "không cô lập quyền giữa các collection, trạng thái 'Indexed' gán cứng trên giao diện. Điểm tốt: giới hạn kích thước nội "
                       "dung trả về, hiển thị bằng textContent nên an toàn XSS.",
        "test_intro": "Test case dựa trên REQ-DOC-01..04, dùng phân hoạch tương đương (collection tồn tại/không tồn tại, artifact tồn tại/không), "
                      "giá trị biên (256 ký tự, max_tokens=0), đoán lỗi (xóa hai lần, sai collection) và kiểm thử tính nhất quán/cô lập dữ liệu.",
        "ui": "Kiểm thử giao diện kiểm tra thông tin từng dòng tài liệu, đồng bộ bằng nút Refresh, hủy/xác nhận xóa qua hộp thoại confirm, menu thao "
              "tác theo Style Guide, trạng thái lập chỉ mục và trạng thái rỗng.",
        "images": [("UI_VINH_01", "UI_VINH_01 – Danh sách tài liệu với tên, collection, badge và nút Delete"),
                   ("UI_VINH_04", "UI_VINH_04 – Sau khi xác nhận xóa, tài liệu biến mất khỏi danh sách")],
        "unit": "Tập trung vào các lớp tương đương và giá trị biên của hai trường collection/artifact.",
        "blackbox": "Kiểm thử hộp đen bao gồm cả kiểm tra hậu điều kiện: sau khi xóa, gọi lại list và semantic-search để chắc chắn nội dung không còn được truy xuất.",
        "extra": [
            ("Kiểm thử tính nhất quán dữ liệu: ", "sau khi xóa, nội dung không còn xuất hiện trong kết quả tìm kiếm ngữ nghĩa (BB_VINH_09 – Pass)."),
            ("Kiểm thử cô lập dữ liệu: ", "tài liệu ở collection nhom11_b không lộ sang nhom11 (BB_VINH_14 – Pass), nhưng xóa với sai collection làm request treo (BUG-09)."),
            ("Kiểm thử hiệu năng: ", "100 request liệt kê với 20 luồng đồng thời (PERF_LIST) – xem bảng hiệu năng ở Phần 1."),
            ("Kiểm thử tự động: ", "test UI tự xử lý hộp thoại confirm (accept/dismiss) và đối chiếu kết quả với API."),
        ],
        "evaluation": [
            "Đánh giá: các thao tác cơ bản (liệt kê, xem nội dung, xóa có xác nhận, cô lập theo collection) hoạt động đúng. Các lỗi tập trung ở "
            "nhánh ngoại lệ: mã lỗi sai ngữ nghĩa (400/500 thay vì 404), xóa hai lần gây lỗi 500, xóa với sai collection làm treo request, tên "
            "collection không được kiểm tra, giao diện thiếu trạng thái thực và thao tác Preview/Search. Ngoài ra danh sách tài liệu bị mất mục "
            "khi có nạp đồng thời (liên quan BUG-01).",
            "Đề xuất: trả 404 cho tài liệu không tồn tại và làm xóa idempotent; thêm timeout phía server cho thao tác xóa; sửa 'return' thành "
            "'continue' trong get_ingested_files; thêm phân trang/sắp xếp; hiển thị trạng thái lấy từ server; bổ sung Preview dùng /v1/artifacts/content.",
        ],
    },
    "DUY": {
        "scope": "Hỏi đáp RAG có trích dẫn là giá trị cốt lõi mà người dùng cảm nhận được. Ngoài tính đúng của phần mềm (request hợp lệ, mã lỗi), "
                 "chức năng này cần được đánh giá về chất lượng AI: trả lời đúng theo tài liệu, không bịa (hallucination), tuân thủ phạm vi truy "
                 "xuất, trích dẫn đúng nguồn, chống prompt injection và trả lời đúng ngôn ngữ.",
        "spec_review": "PRD đặc tả rất chi tiết cách xây request (semantic_search + ingested_artifact) và cách hiển thị trích dẫn (nút số, popup, ghép "
                       "nodes[].id). Tuy nhiên tài liệu không có bất kỳ tiêu chí chất lượng câu trả lời nào (độ chính xác, không bịa), không quy định "
                       "ngôn ngữ trả lời và không nêu yêu cầu mô hình phải hỗ trợ tool calling – thiếu sót trực tiếp dẫn tới BUG-15.",
        "code_review": "Review chat_router.py, chat_models.py, semantic_search_builder.py, artifact_refs.py và bộ phân tích trích dẫn. Điểm tốt: lọc "
                       "phạm vi truy xuất theo collection/artifacts đúng, bộ parser trích dẫn có 19 test robustness. Điểm yếu: model không bắt buộc, "
                       "max_tokens ≤ 0 bị bỏ qua, công cụ từ chối tham số sai thay vì tự phục hồi, thẻ <citation> do mô hình sinh được tin tưởng, "
                       "không có ranh giới dữ liệu không tin cậy trong prompt, ánh xạ lỗi LLM sai mã HTTP, streaming trích dẫn O(n²).",
        "test_intro": "Bộ câu hỏi kiểm thử được thiết kế theo bảng quyết định: mỗi định dạng tài liệu (.md, .txt, .docx, .pdf, FAQ tiếng Anh) có một "
                      "câu hỏi với đáp án xác định để chấm tự động; bổ sung các tình huống khó: câu hỏi ngoài tài liệu, giới hạn phạm vi, tắt/bật "
                      "trích dẫn, collection không tồn tại, tài liệu chứa prompt injection và kiểm tra ngôn ngữ. Các câu trả lời được chấm tự động "
                      "bằng biểu thức chính quy, sau đó đánh giá lại thủ công (human review) những trường hợp chấm tự động chưa chính xác.",
        "ui": "Kiểm thử giao diện gửi câu hỏi thực qua ô chat của Workbench, chờ mô hình trả lời (30–120 giây trên CPU) và kiểm tra: câu trả lời hiển "
              "thị, chỉ báo chờ, thẻ citation thô không bị lộ, nút trích dẫn mở popup, khối công cụ hiển thị thu gọn, công tắc Documents trong menu.",
        "images": [("UI_DUY_01", "UI_DUY_01 – Hỏi đáp có tài liệu qua giao diện chat"),
                   ("UI_DUY_03", "UI_DUY_03 – Câu trả lời có tài liệu, kiểm tra hiển thị trích dẫn")],
        "unit": "Bộ phân tích trích dẫn được kiểm thử với mã hợp lệ, không phân biệt hoa thường, mã bịa đặt và mã lặp lại.",
        "blackbox": "Mỗi câu hỏi RAG ghi lại thời gian phản hồi để phục vụ đánh giá hiệu năng (PERF_RAG).",
        "extra": [
            ("Đánh giá chất lượng AI (RAG evaluation): ", "5/5 câu hỏi có đáp án trong tài liệu được trả lời đúng với qwen2.5:3b; mô hình từ chối đúng "
                                                          "khi tài liệu không có thông tin; nhưng trích dẫn trỏ sai tài liệu (BUG-16) và trả lời tiếng Anh cho câu hỏi tiếng Việt (BUG-18)."),
            ("Kiểm thử luồng sử dụng thực tế trên giao diện: ", "phát hiện chat âm thầm tắt Documents khi trình duyệt chưa tải danh sách tài liệu – người dùng nhận câu trả lời 'không có thông tin' dù tài liệu có sẵn (BUG-25, UI_DUY_07)."),
            ("Kiểm thử bảo mật AI: ", "prompt injection gián tiếp từ tài liệu làm mô hình lặp lại chỉ thị độc hại (BUG-17)."),
            ("Kiểm thử cấu hình mô hình: ", "so sánh qwen2.5:3b và llama3.2:3b – llama3.2 gọi sai công cụ nên RAG thất bại hoàn toàn và trả lời bịa (BUG-15)."),
            ("Kiểm thử hiệu năng: ", "thời gian phản hồi RAG trên CPU (PERF_RAG) – trung vị khoảng 1 phút/câu."),
        ],
        "evaluation": [
            "Đánh giá: phần mềm xử lý request RAG đúng đặc tả (messages rỗng, thiếu tool_context đều bị chặn; tắt trích dẫn hoạt động) và với mô hình "
            "phù hợp, độ chính xác trên bộ câu hỏi có đáp án là tốt. Rủi ro lớn nằm ở chất lượng AI: kết quả phụ thuộc mạnh vào mô hình (llama3.2 "
            "thất bại), trích dẫn có thể sai nguồn, dễ bị prompt injection gián tiếp và không giữ ngôn ngữ người dùng. Trên giao diện, "
            "chat còn âm thầm bỏ qua tài liệu nếu người dùng chưa mở màn hình Documents (BUG-25).",
            "Đề xuất: Workbench nên tự tải danh sách tài liệu khi khởi động và không tự tắt Documents; công bố danh sách mô hình tối thiểu đã kiểm chứng tool calling; công cụ semantic_search nên bỏ qua tham số artifacts không hợp lệ "
            "thay vì từ chối; kiểm tra câu trích dẫn có nằm trong đoạn nguồn; bọc ngữ cảnh truy xuất bằng delimiter 'dữ liệu không tin cậy'; thêm "
            "chỉ dẫn trả lời theo ngôn ngữ câu hỏi vào system prompt mặc định; xây bộ đánh giá RAG tự động (faithfulness, answer relevancy) trong CI.",
        ],
    },
    "MANH": {
        "scope": "Chức năng quản lý hội thoại, mô hình và cấu hình quyết định trải nghiệm sử dụng hằng ngày và an toàn thông tin phía trình duyệt. "
                 "Phạm vi gồm GET /v1/models, /v1/models/{id}, /v1/messages (nhiều lượt, streaming, system prompt, tham số sinh), "
                 "/v1/messages/count_tokens, /v1/messages/validate và các màn hình Sidebar (New Chat, đổi tên, xóa), model dropdown, Settings, API Debugger.",
        "spec_review": "Yêu cầu CRUD hội thoại, lưu localStorage, Enter/Shift+Enter, API Debugger được đặc tả rõ ràng và kiểm thử được. Tuy nhiên có "
                       "nhiều mâu thuẫn: URL mặc định 8001 so với 8080, 'bearer token' so với 'chỉ Basic auth', Thinking Button trong Style Guide; "
                       "không quy định kiểm tra định dạng Base URL và không đề cập bộ gõ tiếng Việt (IME).",
        "code_review": "Review models_router.py, models_service.py, chat_router.py (count_tokens/validate) và phần Settings/Sidebar/Debugger trong "
                       "index.html (8.210 dòng). Điểm tốt: phân trang /v1/models có ràng buộc, che header Authorization trong Debugger, kiểm tra đủ "
                       "cặp username/password, cắt tiêu đề dài. Điểm yếu: mật khẩu lưu plaintext trong localStorage, không kiểm tra Base URL, không "
                       "xử lý lỗi quota localStorage, không kiểm tra isComposing cho IME, model không tồn tại trả 400, toàn bộ UI dồn trong một "
                       "file khó bảo trì và không có unit test JavaScript.",
        "test_intro": "Test case dựa trên REQ-SES-01..04 và tiêu chí MVP 1–7, 17–18, 23 của PRD; dùng phân hoạch tương đương, giá trị biên (limit=0/1, "
                      "temperature 0/1/1.5/-0.1, max_tokens=0), kiểm thử hội thoại nhiều lượt, streaming SSE và kiểm thử bảo mật phía client.",
        "ui": "Kiểm thử giao diện tự động các thao tác New Chat, đổi tên, cắt tiêu đề dài, xóa có xác nhận, lưu sau reload, dropdown mô hình, "
              "Shift+Enter, kiểm tra Base URL, Basic auth, che thông tin trong API Debugger, lưu mật khẩu và giao diện di động 375px.",
        "images": [("UI_MANH_06", "UI_MANH_06 – Dropdown chọn mô hình lấy từ /v1/models"),
                   ("UI_MANH_08", "UI_MANH_08 – Base URL 'abc xyz' vẫn được lưu, không có cảnh báo")],
        "unit": "Kiểm thử biên các tham số sinh và ràng buộc vai trò tin nhắn cuối.",
        "blackbox": "Bao gồm kiểm thử streaming: đọc luồng SSE và kiểm tra thứ tự sự kiện message_start … message_stop.",
        "extra": [
            ("Kiểm thử bảo mật phía client: ", "Debugger không lộ chuỗi Basic auth (Pass) nhưng mật khẩu lưu dạng rõ trong localStorage (BUG-20)."),
            ("Kiểm thử responsive: ", "ở độ rộng 375px không có cuộn ngang, ô chat vẫn dùng được (UI_MANH_12 – Pass)."),
            ("Kiểm thử hiệu năng: ", "50 request tuần tự /v1/models (PERF_MODELS) và thời gian phản hồi câu hỏi đơn (BB_MANH_16)."),
            ("Kiểm thử tự động: ", "Playwright tự đóng/mở mục Authentication, tự xử lý dialog, đọc localStorage để kiểm chứng."),
        ],
        "evaluation": [
            "Đánh giá: quản lý hội thoại phía giao diện hoạt động tốt và đúng PRD (tạo, đổi tên, xóa, lưu sau reload, cắt tiêu đề, Shift+Enter, "
            "responsive); API mô hình/hội thoại đúng đặc tả ở hầu hết trường hợp, kể cả hội thoại nhiều lượt và streaming. Các lỗi chủ yếu là kiểm "
            "tra đầu vào (Base URL, max_tokens=0), mã lỗi sai ngữ nghĩa (400 thay vì 404), bảo mật mật khẩu trong localStorage và việc không phát "
            "hiện mô hình mới khi server đang chạy.",
            "Đề xuất: kiểm tra Base URL bằng new URL() và chỉ cho http/https; lưu mật khẩu trong sessionStorage hoặc chỉ trong bộ nhớ; trả 404 cho mô "
            "hình không tồn tại; từ chối max_tokens ≤ 0; nút 'Refresh models' nên gọi lại auto-discover phía server; tách index.html thành module để "
            "viết unit test JavaScript.",
        ],
    },
}

PART3 = {
    "sections": [
        ("3.1. Kết luận", [
            "Nhóm đã hoàn thành đầy đủ các yêu cầu của bài tập: chọn một hệ thống RAG mã nguồn mở phổ biến trên GitHub (PrivateGPT, ~57,6 nghìn sao), "
            "cài đặt và chạy được trên môi trường của nhóm, review tài liệu đặc tả theo checklist, review code từng chức năng, xây dựng và thực thi "
            "test case giao diện, đơn vị, hộp đen cho 4 chức năng, cùng các nội dung lựa chọn thêm (kiểm thử tự động, bảo mật, hiệu năng, đồng thời, "
            "đánh giá chất lượng AI và ứng dụng công cụ AI).",
            "Kết quả cho thấy PrivateGPT hoạt động tốt ở luồng chính khi dùng tuần tự với mô hình hỗ trợ tool calling, nhưng còn nhiều lỗi ở nhánh "
            "ngoại lệ, bảo mật đầu vào, xử lý đồng thời và tương thích Windows; tài liệu đặc tả thiếu yêu cầu phi chức năng và có nhiều mâu thuẫn.",
        ]),
        ("3.2. Đề xuất cải tiến cho dự án", [
            ("Ưu tiên 1 – Toàn vẹn dữ liệu: ", "khóa/giao dịch khi cập nhật trạng thái tài liệu, sửa lỗi mất dữ liệu khi nạp đồng thời (BUG-01)."),
            ("Ưu tiên 1 – Bảo mật: ", "ràng buộc ký tự artifact/collection, whitelist URI, không lưu mật khẩu plaintext, đánh dấu ngữ cảnh RAG là dữ liệu không tin cậy."),
            ("Ưu tiên 2 – Tương thích: ", "thêm runner Windows vào CI; import celery/fcntl có điều kiện; đọc file với encoding='utf-8'; hỗ trợ Qdrant local trên Windows."),
            ("Ưu tiên 2 – Chất lượng AI: ", "danh sách mô hình đã kiểm chứng, bộ đánh giá RAG tự động, kiểm tra trích dẫn, trả lời theo ngôn ngữ người dùng."),
            ("Ưu tiên 3 – Tài liệu: ", "bổ sung NFR, mã yêu cầu, bảng mã lỗi; sửa các mâu thuẫn DOC-01..DOC-16."),
        ]),
        ("3.3. Bài học kinh nghiệm của nhóm", [
            "Kiểm thử ứng dụng RAG cần kết hợp kiểm thử phần mềm truyền thống với đánh giá chất lượng mô hình: cùng một mã nguồn nhưng đổi mô hình "
            "(llama3.2 → qwen2.5) cho kết quả hoàn toàn khác.",
            "Kết quả chấm tự động bằng regex cho câu trả lời AI cần được người kiểm thử xem lại; nhóm đã đánh giá lại thủ công 3 test case.",
            "Nhiều lỗi nghiêm trọng (mất dữ liệu khi nạp đồng thời, treo request) chỉ lộ ra khi chạy song song nhiều bộ test – cần đưa kiểm thử "
            "đồng thời vào kế hoạch ngay từ đầu.",
            "CI chỉ chạy trên một hệ điều hành sẽ bỏ sót cả một lớp lỗi tương thích, dù dự án có hơn 2.000 test.",
        ]),
    ],
    "deliverables": [
        ["Kết quả Review (cả nhóm)", "01_KetQua_Review_Nhom11.xlsx", "Checklist tài liệu, lỗi tài liệu, review đặc tả từng chức năng, review code 4 thành viên, tổng hợp"],
        ["Kết quả kiểm thử", "02_KetQua_KiemThu_Nhom11.xlsx", "Kế hoạch, lỗi môi trường, test case & kết quả 4 thành viên, báo cáo lỗi, hiệu năng, truy vết, tổng hợp"],
        ["Báo cáo", "BTLSo1.docx", "Báo cáo theo bố cục yêu cầu"],
        ["Tài liệu bổ sung", "03_MinhChung/DacTa_YeuCau_BoSung_Nhom11.docx", "Use case, mã yêu cầu, yêu cầu phi chức năng"],
        ["Mã nguồn hệ thống", "https://github.com/zylon-ai/private-gpt (commit 42ce052) – bản sao: source_code/", "Hệ thống được kiểm thử"],
        ["Script kiểm thử", "03_MinhChung/test_scripts/", "unit/, ui/ (Playwright), blackbox/, performance/, report_gen/"],
        ["Minh chứng", "03_MinhChung/logs/, screenshots/, test_data/", "Kết quả JSON/XML, log server, ảnh chụp giao diện, dữ liệu kiểm thử"],
        ["Hướng dẫn chạy", "source_code/run_nhom11.ps1, settings-nhom11.yaml", "Khởi động hệ thống trên Windows"],
    ],
    "contrib": [
        ["Nguyễn Minh Tiến", "Điều phối review; khảo sát, chọn hệ thống", "Nạp tài liệu: review, {UI_TIEN} TC UI, {UT_TIEN} TC unit, {BB_TIEN} TC hộp đen, bảo mật, đồng thời", "25%"],
        ["Nguyễn Bá Quang Vinh", "Reviewer; dựng dữ liệu kiểm thử", "Quản lý tài liệu: review, {UI_VINH} TC UI, {UT_VINH} TC unit, {BB_VINH} TC hộp đen, nhất quán dữ liệu", "25%"],
        ["Vũ Đức Duy", "Reviewer; đặc tả bổ sung NFR", "Hỏi đáp RAG: review, {UI_DUY} TC UI, {UT_DUY} TC unit, {BB_DUY} TC hộp đen, đánh giá chất lượng AI", "25%"],
        ["Bùi Văn Mạnh", "Thư ký review; cài đặt môi trường", "Hội thoại & cấu hình: review, {UI_MANH} TC UI, {UT_MANH} TC unit, {BB_MANH} TC hộp đen, hiệu năng", "25%"],
    ],
}
