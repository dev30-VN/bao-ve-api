# 🛡️ Đề tài B14: Bảo vệ API – Ký yêu cầu HMAC, Giới hạn tần suất & Chống phát lại

**Môn học:** Bảo mật thông tin (CMP174) – Hệ Đào tạo Từ xa  
**Trường:** Đại học Công nghệ TP.HCM (HUTECH) – Khoa Công nghệ Thông tin

---

## 👥 Thành viên nhóm & Phân công vai trò

| STT | Họ và tên        |     MSSV     | Vai trò                                                      | Thư mục phụ trách       |
| :-: | :--------------- | :----------: | :----------------------------------------------------------- | :---------------------- |
|  1  | [Nguyễn Văn Lợi] | [2410060398] | **Lead Developer** (Xây dựng hệ thống API & Security)        | `server/`, `client/`    |
|  2  | [Bùi Văn Hùng]   | [2410060419] | **Security QA & Benchmarking** (Kiểm thử & Đo lường)         | `tests/`, `benchmarks/` |
|  3  | [Lê Đình Ngọc]   | [2410060428] | **Technical Writer & Video Editor** (Báo cáo, Slide & Video) | `docs/`                 |

---

## ⚙️ 1. Hướng dẫn cài đặt & Chạy hệ thống

### Yêu cầu môi trường

- Python 3.10+
- Git

### Các bước cài đặt & khởi chạy

1. **Clone repository về máy:**

   ```bash
   git clone [https://github.com/dev30-VN/bao-ve-api.git](https://github.com/dev30-VN/bao-ve-api.git)
   cd bao-ve-api
   ```

2. **Tạo và kích hoạt môi trường ảo (Virtual Environment):**

   - **Trên Windows (PowerShell):**
     _(Chạy lệnh mở khóa quyền thực thi script 1 lần duy nhất trên máy nếu gặp lỗi `UnauthorizedAccess`)_

     ```powershell
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

     _Kiểm tra thành công:_ Đầu dòng lệnh hiện chữ `(venv)` màu xanh.

   - **Trên macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Cài đặt các thư viện cần thiết:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi chạy API Server:**
   ```bash
   uvicorn server.main:app --reload
   ```
   - Truy cập tài liệu API tương tác (Swagger UI) tại: `http://127.0.0.1:8000/docs`
   - **Tài khoản / API Key demo:**
     - `X-API-Key`: `client_app_01`
     - `Secret Key`: Xem cấu hình mẫu trong `server/security.py` (không đưa khóa thật lên môi trường production).

---

## 🤝 2. Quy tắc làm việc trên GitHub (BẮT BUỘC CHO CẢ 3 THÀNH VIÊN)

Để đảm bảo lịch sử commit minh bạch và tránh xung đột mã nguồn (merge conflict), tất cả thành viên **bắt buộc** tuân thủ quy trình **GitHub Flow** sau:

### Bước A: Khai báo thông tin Git (Chỉ làm 1 lần duy nhất trước khi bắt đầu)

Mỗi thành viên mở Terminal tại thư mục dự án và chạy 2 lệnh sau bằng **tên và email tài khoản GitHub cá nhân** của mình (để GitHub ghi nhận đúng người đóng góp):

```bash
git config --global user.name "Ten_Tai_Khoan_GitHub_Cua_Ban"
git config --global user.email "email_dang_ky_github_cua_ban@gmail.com"
```

### Bước B: Quy tắc bảo vệ nhánh `main` (Không tự ý Merge)

- 🚫 **Tuyệt đối không push code trực tiếp lên nhánh `main`.**
- 🚫 **Không tự ý bấm Merge Pull Request của chính mình.** Khi tạo Pull Request (PR), phải gắn thẻ (Reviewers) một thành viên khác trong nhóm để kiểm tra và bấm nút **Merge pull request**.
- 🔒 **Bảo mật thông tin:** Không đẩy file `.env`, khóa bí mật thật hoặc thư mục `venv/` lên repository.

### Bước C: Quy trình đẩy code mỗi ngày

Mỗi khi bắt đầu làm việc hoặc cập nhật tính năng/tài liệu mới, thực hiện đúng **4 bước** sau:

1. **Cập nhật code mới nhất từ nhánh `main` về máy:**

   ```bash
   git checkout main
   git pull origin main
   ```

2. **Tạo một nhánh riêng mới cho phần việc của mình:**
   _(Đặt tên nhánh theo quy ước: `feat/ten-tinh-nang`, `test/ten-kich-ban`, hoặc `docs/ten-tai-lieu`)_

   ```bash
   git checkout -b ten-nhanh-cua-ban
   ```

3. **Lưu thay đổi (Commit) và đẩy nhánh lên GitHub:**

   ```bash
   git add .
   git commit -m "mo ta ngan gon cong viec vua lam"
   git push -u origin ten-nhanh-cua-ban
   ```

4. **Tạo Pull Request (PR) & Nhờ đồng đội Merge:**
   - Truy cập `https://github.com/dev30-VN/bao-ve-api` -> bấm nút xanh **`Compare & pull request`**.
   - Chọn **Reviewers** là 1 thành viên khác trong nhóm -> bấm **`Create pull request`**.
   - Nhắn vào nhóm chat để đồng đội vào kiểm tra và bấm **Merge** vào nhánh `main`.
