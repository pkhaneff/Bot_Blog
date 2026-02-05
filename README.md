# 🤖 RAG Chatbot Application

Chào mừng bạn đến với dự án **RAG Chatbot**. Đây là một ứng dụng Chatbot thông minh được xây dựng để trả lời câu hỏi dựa trên kho dữ liệu tài liệu riêng của bạn (files PDF, Word, Text). Hệ thống sử dụng công nghệ AI tiên tiến để "hiểu" tài liệu và trả lời tự nhiên như người thật.

## 🚀 Công Nghệ Sử Dụng (Tech Stack)

Dự án được xây dựng trên nền tảng các công nghệ hiện đại và mạnh mẽ:

*   **Ngôn ngữ chính**: [Python](https://www.python.org/) - Ngôn ngữ hàng đầu cho AI & Backend.
*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Framework hiệu năng cao để xây dựng API.
*   **AI Engine**: [LangChain](https://www.langchain.com/) - "Nhạc trưởng" kết nối các mô hình AI.
*   **LLM (Trí tuệ nhân tạo)**: [OpenAI (GPT)](https://openai.com/) - Bộ não xử lý ngôn ngữ và trả lời câu hỏi.
*   **Cơ sở dữ liệu tìm kiếm (Vector DB)**: [OpenSearch](https://opensearch.org/) - Giúp tìm kiếm thông tin ngữ nghĩa cực nhanh.
*   **Cơ sở dữ liệu quan hệ**: [PostgreSQL](https://www.postgresql.org/) - Lưu trữ lịch sử chat và trạng thái hệ thống.
*   **Container**: [Docker](https://www.docker.com/) - Giúp đóng gói và chạy ứng dụng dễ dàng mọi nơi.

---

## ⚙️ Hướng Dẫn Cài Đặt

Có 2 cách để bạn chạy dự án này:

### Cách 1: Chạy bằng Docker (Khuyên dùng)
Đây là cách đơn giản nhất, bạn không cần cài đặt Python hay Database thủ công.

1.  **Cài đặt Docker Desktop**: [Tải tại đây](https://www.docker.com/products/docker-desktop).
2.  **Cấu hình môi trường**:
    *   Tạo file `.env` từ file mẫu (nếu có).
    *   Điền `OPENAI_API_KEY` và các thông tin Database cần thiết.
3.  **Khởi chạy**:
    Mở terminal tại thư mục dự án và chạy câu lệnh:
    ```bash
    docker-compose up --build
    ```
    Ứng dụng sẽ tự động tải các thành phần và khởi chạy tại `http://localhost:8090`.

### Cách 2: Chạy Thủ công (Dành cho Dev)
1.  **Cài đặt Python 3.10+**.
2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Cài đặt Database**: Bạn cần tự cài đặt và chạy PostgreSQL và OpenSearch riêng lẻ.
4.  **Chạy ứng dụng**:
    ```bash
    python -m app.main
    ```

---

## 💡 Luồng Hoạt Động Của Hệ Thống

Để hiểu cách Chatbot này vận hành, hãy tưởng tượng nó giống như một **Thủ thư thông minh** trong thư viện.

### 1. Giai Đoạn "Học Bài" (Nạp Dữ Liệu)
Trước khi có thể trả lời, Chatbot cần được cung cấp kiến thức:
1.  **Gửi tài liệu**: Bạn tải lên các file (PDF, Word, Text) chứa kiến thức cần thiết.
2.  **Đọc & Tách nhỏ**: Hệ thống đọc nội dung và chia nhỏ văn bản thành các đoạn ngắn (để dễ nhớ và tìm kiếm).
3.  **Mã hóa (Embedding)**: Mỗi đoạn văn bản được chuyển đổi thành một dãy số đặc biệt (vector) biểu diễn ý nghĩa của nó.
4.  **Lưu trữ**: Các dãy số này được cất vào "Bộ nhớ dài hạn" (OpenSearch) để tra cứu sau này.

### 2. Giai Đoạn "Trả Lời" (Chat)
Khi bạn đặt một câu hỏi:
1.  **Tiếp nhận**: Hệ thống nhận câu hỏi của bạn.
2.  **Tra cứu**: "Thủ thư" sẽ tìm nhanh trong "Bộ nhớ dài hạn" những đoạn văn bản có ý nghĩa *liên quan nhất* đến câu hỏi.
3.  **Tổng hợp**: Hệ thống gom câu hỏi của bạn + những thông tin vừa tìm được + ngữ cảnh cuộc trò chuyện cũ.
4.  **Suy luận (AI)**: Toàn bộ thông tin được gửi cho "Bộ não" (OpenAI). AI sẽ đọc hiểu thông tin đó và tự viết ra câu trả lời phù hợp nhất.
5.  **Phản hồi**: Câu trả lời được gửi lại cho bạn ngay lập tức.

