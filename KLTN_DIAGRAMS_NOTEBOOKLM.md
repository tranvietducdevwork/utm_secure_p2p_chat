# Hướng dẫn vẽ lại sơ đồ cho KLTN (NotebookLM / draw.io)

NotebookLM **không upload được file `.py`**. Dùng một trong các cách sau.

## Cách 1 — Upload file `.txt` (khuyến nghị)

1. Mở [NotebookLM](https://notebooklm.google.com) → **New notebook**
2. **Add source** → chọn file:
   ```
   /Users/tranvietduc/Desktop/KLTN/secure_p2p_chat/KLTN_SO_DO_NGUON.txt
   ```
3. Trong chat NotebookLM, gõ prompt (mỗi hình một lần), ví dụ:
   > Dựa trên nguồn Hình 2.4, vẽ sequence diagram luồng gửi tin E2E relay. Server không giải mã ciphertext. Xuất dạng sơ đồ rõ ràng, có nhãn tiếng Việt.

4. Lưu ảnh / chụp màn hình → chèn vào Word thay sơ đồ ASCII.

## Cách 2 — Google Docs

1. Mở `KLTN_SO_DO_NGUON.txt` → copy toàn bộ
2. Dán vào **Google Docs** mới → lưu
3. NotebookLM → **Add source** → chọn Google Doc đó

## Cách 3 — Dán trực tiếp (không upload file)

1. NotebookLM → **Add source** → **Copied text**
2. Copy một phần từ `KLTN_SO_DO_NGUON.txt` (ví dụ chỉ Hình 2.2 + prompt)
3. Dán vào → dùng prompt vẽ hình tương ứng

## Cách 4 — PDF

1. Mở `KLTN_SO_DO_NGUON.txt` trong Word hoặc Pages
2. **Export PDF**
3. Upload PDF vào NotebookLM

## Cách 5 — draw.io (không cần NotebookLM)

1. Vào [draw.io](https://app.diagrams.net/)
2. Copy sơ đồ ASCII từ Word hoặc từ `KLTN_SO_DO_NGUON.txt`
3. Vẽ lại bằng shape UML → Export PNG → chèn Word

---

## Danh sách hình cần có trong bản in

| Mã hình | Nội dung | Nguồn |
|---------|----------|-------|
| Hình 1.1 | Kiến trúc tổng quan | KLTN_SO_DO_NGUON.txt |
| Hình 2.1 | Ngữ cảnh hệ thống | KLTN_SO_DO_NGUON.txt |
| Hình 2.2 | Luồng đăng ký | KLTN_SO_DO_NGUON.txt |
| Hình 2.3 | Luồng vào phòng | KLTN_SO_DO_NGUON.txt |
| Hình 2.4 | Luồng gửi tin E2E | KLTN_SO_DO_NGUON.txt |
| Hình 2.5 | Cấu trúc Flutter | KLTN_SO_DO_NGUON.txt |
| Hình 2.6 | Cấu trúc Server | KLTN_SO_DO_NGUON.txt |
| Hình 2.7 | Sequence chat | KLTN_SO_DO_NGUON.txt |
| Hình 2.8 | CSDL SQLite | KLTN_SO_DO_NGUON.txt |
| Hình 3.x | Screenshot app + /health | Chụp màn hình thực tế |

---

## Chạy lại sinh Word

```bash
cd /Users/tranvietduc/Desktop/KLTN/secure_p2p_chat
python3 generate_kltn.py
```

Output: `/Users/tranvietduc/Downloads/KLTN_Tran_Viet_Duc_P2P_Chat.docx`
