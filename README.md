# Secure P2P Chat

Ứng dụng nhắn tin bảo mật thời gian thực với **mã hóa đầu cuối (E2E)**. Server chỉ làm signaling — **không lưu nội dung tin nhắn**.

## Luồng sử dụng (4G / WiFi)

1. **Đăng ký / đăng nhập** trên 2 điện thoại (không cần nhập IP LAN)
2. Cả hai **nhập cùng mã phòng** (ví dụ `PHONG01`)
3. Thấy nhau trong phòng → bấm vào tên → **chat E2E**

Tin nhắn qua mạng di động dùng **relay đã mã hóa** qua server cloud (P2P trực tiếp thường không khả thi qua 4G/NAT).

## Deploy signaling server lên cloud (bắt buộc cho 4G/WiFi)

### Render (miễn phí)

**Quan trọng:** Repo có file Python (`generate_kltn.py`) ở thư mục gốc — Render sẽ **nhận nhầm là Python** nếu không cấu hình đúng.

#### Cách A — Sửa service hiện tại (Settings)

Vào service trên Render → **Settings** → **Build & Deploy**, sửa:

| Ô | Giá trị |
|---|--------|
| **Language** (hoặc Runtime) | **Node** (KHÔNG chọn Python) |
| **Root Directory** | `signaling_server` |
| **Build Command** | `npm install` |
| **Start Command** | `npm start` |

**Environment** → thêm:

| Key | Value |
|-----|--------|
| `JWT_SECRET` | `utm-kltn-secret-2026-abc` |

Save → **Manual Deploy**.

#### Cách B — Tạo mới bằng Blueprint (khuyên dùng)

1. [render.com](https://render.com) → **New** → **Blueprint**
2. Chọn repo `utm_secure_p2p_chat`
3. Render đọc `render.yaml` tự động (Node + `signaling_server`)

#### Kiểm tra deploy thành công

Mở `https://YOUR-APP.onrender.com/health` — phải thấy JSON `{"status":"ok",...}`

Copy URL dạng `https://xxx.onrender.com` đưa vào Flutter app.

### Cấu hình URL trong Flutter

Sửa file `flutter_app/lib/config/app_config.dart`:

```dart
static const cloudSignalingUrl = String.fromEnvironment(
  'SIGNALING_URL',
  defaultValue: 'https://xxx.onrender.com', // URL sau khi deploy
);
```

Hoặc build với:

```bash
flutter run --dart-define=SIGNALING_URL=https://xxx.onrender.com
```

### Test nhanh với ngrok (không deploy)

```bash
cd signaling_server && npm start
# Terminal khác:
ngrok http 3000
```

Dùng URL `https://xxxx.ngrok-free.app` làm `SIGNALING_URL`.

## Chạy local (emulator)

```bash
cd signaling_server && npm install && npm start

cd flutter_app
flutter run --dart-define=SIGNALING_URL=http://10.0.2.2:3000   # Android emulator
# hoặc
flutter run --dart-define=SIGNALING_URL=http://127.0.0.1:3000   # iOS simulator
```

## Kiến trúc

- **Flutter app**: UI, WebRTC, mã hóa X25519 + AES-GCM, SQLite local, **phòng chat theo mã**
- **Signaling server**: JWT auth, relay ICE/SDP + tin nhắn E2E trong cùng phòng

## Demo trước hội đồng

Mở trên trình duyệt: `https://utm-secure-p2p-chat.onrender.com/health`

### Kịch bản trình bày

1. **Chế độ mặc định (E2E)** — App → icon 🧪 → tắt hết toggle → 2 máy chat → `/health` → `Tin nhắn lưu: 0`
2. **Lưu bản mã hóa** — Bật "Server lưu tin nhắn" → chat → `/health` thấy bảng ciphertext → **Đọc được? Không**
3. **Lưu plaintext (so sánh)** — Bật thêm "Lưu plaintext" → chat → `/health` thấy nội dung rõ → **Hacker đọc được**

### Câu hỏi hội đồng: Hack DB server có đọc được tin nhắn?

| Dữ liệu trên server | Đọc được? |
|---------------------|-----------|
| Chế độ E2E mặc định | Không — server không lưu tin nhắn |
| Lưu ciphertext (demo) | Không — chỉ thấy chuỗi mã hóa |
| Lưu plaintext (demo) | Có — mô phỏng chat server truyền thống |
| SQLite trên điện thoại | Có — tin nhắn lưu local trên máy user |


```bash
python3 generate_kltn.py
```

Output: `KLTN_Tran_Viet_Duc_P2P_Chat.docx`
